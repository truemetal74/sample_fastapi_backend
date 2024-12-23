import logging
from datetime import datetime, timedelta, UTC
from typing import Final, Iterator, Optional, Dict

from app_config import AppConfig
from bss.adapters import BSSAdapter
from bss.dbs import TiedKeyValue
from bss.models import DeliveryChannel, SipServer, UserCreateResponse, CustomRequest, CustomResponse
from bss.types import (
    CallRecordingId,
    Capabilities,
    CDRInfo,
    ContactInfo,
    EndUser,
    OTPCreateResponse,
    OTPVerifyRequest,
    SessionInfo,
    UserInfo,
    safely_extract_scalar_value,
    UserVoicemailsResponse,
    UserVoicemailMessagePatch,
    VoicemailMessageDetails,
    SIPRegistrationStatus
)
from report_error import WebTritErrorException
from .api import AccountAPI, AdminAPI
from .config import Settings
from .serializer import Serializer
from .types import (
    PortaSwitchSignInCredentialsType,
    PortaSwitchContactsSelectingMode,
    PortaSwitchDualVersionSystem,
    PortaSwitchMailboxMessageFlag,
    PortaSwitchMailboxMessageFlagAction,
    PortaSwitchMailboxMessageAttachmentFormat,
)
from .utils import generate_otp_id, extract_fault_code


class PortaSwitchAdapter(BSSAdapter):
    """Connects WebTrit and PortaSwitch. Authenticate a user using his/her data in PortaSwitch,
    retrieve user's SIP credentials to be used by WebTrit and return a list of other configured
    extenstions (to be provided as 'Cloud PBX' contacts).
    Currently does not support OTP login.

    """

    VERSION: Final[str] = "0.1.3"
    OTP_DELIVERY_CHANNEL: Final[DeliveryChannel] = DeliveryChannel.email
    CAPABILITIES: Final[Capabilities] = [
        Capabilities.otpSignin,
        Capabilities.passwordSignin,
        Capabilities.recordings,
        Capabilities.callHistory,
        Capabilities.extensions,
        Capabilities.voicemail,
        Capabilities.customMethods,
        Capabilities.internal_messaging,
        Capabilities.sms_messaging,
    ]

    def __init__(self, config: AppConfig):
        super().__init__(config)

        self._settings = Settings()
        self._portaswitch_settings = self._settings.PORTASWITCH_SETTINGS
        self._otp_settings = self._settings.OTP_SETTINGS

        self._admin_api = AdminAPI(self._portaswitch_settings)
        self._account_api = AccountAPI(self._portaswitch_settings)
        self._sip_server = SipServer(
            host=self._portaswitch_settings.SIP_SERVER_HOST, port=self._portaswitch_settings.SIP_SERVER_PORT
        )

        self._cached_otp_ids = TiedKeyValue()
        self._cached_capabilities = self.calculate_capabilities()

    @classmethod
    def name(cls) -> str:
        """Returns the name of the adapter."""
        return cls.__name__

    @classmethod
    def version(cls) -> str:
        """Returns the version of the adapter."""
        return cls.VERSION

    def get_capabilities(self) -> list[Capabilities]:
        """Returns the capabilities of this API adapter."""
        return self._cached_capabilities

    def authenticate(self, user: UserInfo, password: str = None) -> SessionInfo:
        """Authenticate a PortaSwitch account with login and password and obtain an API token for
        further requests.

        Parameters:
            :user (UserInfo): The information about the account to be logged in.
            :password (str): The password of the account to be verified.

        Returns:
            :(SessionInfo): The object with the obtained session tokens.
        """
        try:
            is_sip_credentials = self._portaswitch_settings.SIGNIN_CREDENTIALS == PortaSwitchSignInCredentialsType.SIP
            login_attr = "id" if is_sip_credentials else "login"
            password_attr = "h323_password" if is_sip_credentials else "password"

            account_info = self._admin_api.get_account_info(**{login_attr: user.login}).get("account_info")
            if not account_info or account_info[password_attr] != password:
                raise WebTritErrorException(401, "User authentication error", code="incorrect_credentials")

            session_data = self._account_api.login(account_info["login"], account_info["password"])

            return SessionInfo(
                user_id=account_info["i_account"],
                access_token=session_data["access_token"],
                refresh_token=session_data["refresh_token"],
                expires_at=datetime.now() + timedelta(seconds=session_data["expires_in"]),
            )

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in (
                "Server.Session.auth_failed",
                "Server.Session.cannot_login_brute_force_activity",
                "Client.Session.check_auth.failed_to_process_access_token",
            ):
                raise WebTritErrorException(
                    status_code=401,
                    error_message="User authentication error",
                )

            raise error

    def generate_otp(self, user: UserInfo) -> OTPCreateResponse:
        """Requests PortaSwitch to generate OTP.

        Parameters:
            :user (UserInfo): The object containing user_ref.

        Returns:
            :(OTPCreateResponse): Information about the created OTP.
                In our case, PortaSwitch does not return any valueable info.
                We return here a dummy otp_id. So, when PortaSwitch supported returning the
                otp_id, we would not break the interface.

        """
        try:
            account_info = self._admin_api.get_account_info(id=user.user_id).get("account_info")
            if not account_info:
                raise WebTritErrorException(404, f"There is no an account with such id: {user.user_id}")

            i_account = account_info["i_account"]
            success: int = self._admin_api.create_otp(i_account, self.OTP_DELIVERY_CHANNEL)["success"]
            if not success:
                raise WebTritErrorException(500, "Unknown error", code="external_api_issue")

            otp_id: str = generate_otp_id()
            self._cached_otp_ids[otp_id] = i_account

            env_info = self._admin_api.get_env_info()

            return OTPCreateResponse(
                otp_id=otp_id, delivery_channel=self.OTP_DELIVERY_CHANNEL, delivery_from=env_info.get("email")
            )

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Server.AccessControl.empty_rec_and_bcc",):
                raise WebTritErrorException(422, "Delivery channel unspecified", code="delivery_channel_unspecified")

            raise error

    def validate_otp(self, otp: OTPVerifyRequest) -> SessionInfo:
        """Requests PortaSwitch to generate OTP.

        Parameters:
            :otp (OTPVerifyRequest): The object containing OTP token to be verified.

        Returns:
            :(OTPCreateResponse): Information about the created OTP.
                In our case, PortaSwitch does not return any valueable info.
                We return here a dummy otp_id. So, when PortaSwitch supported returning the
                otp_id, we would not break the interface.

        """
        try:
            # PortaSwitch API does not operate with otp_id.
            # We need the otp_id only for storing the i_account.
            otp_id = safely_extract_scalar_value(otp.otp_id)

            i_account: int = self._cached_otp_ids.get(otp_id)
            if not i_account:
                raise WebTritErrorException(status_code=404, error_message=f"Incorrect OTP code: {otp.code}")

            data: dict = self._admin_api.verify_otp(otp_token=otp.code)
            if i_account not in self._otp_settings.IGNORE_ACCOUNTS and not data["success"]:
                raise WebTritErrorException(status_code=404, error_message=f"Incorrect OTP code: {otp.code}")

            self._cached_otp_ids.pop(otp_id)

            # Emulate account login.
            account_info: dict = self._admin_api.get_account_info(i_account=i_account)["account_info"]
            session_data: dict = self._account_api.login(account_info["login"], account_info["password"])

            return SessionInfo(
                user_id=account_info["i_account"],
                access_token=session_data["access_token"],
                refresh_token=session_data["refresh_token"],
                expires_at=datetime.now() + timedelta(seconds=session_data["expires_in"]),
            )

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Server.Session.alert_You_must_change_password",):
                raise WebTritErrorException(
                    status_code=422,
                    # code = OTPUserDataErrorCode.validation_error,
                    error_message="Failed to perform authentication using this account."
                    "Try changing this account web-password.",
                )

            raise error

    def validate_session(self, access_token: str) -> SessionInfo:
        """Checks whether the input access_token is valid.

        Parameters:
            :access_token (str): The token used to access PortaSwitch API.

        Returns:
            :(SessionInfo): The object with the obtained session tokens.

        """
        try:
            session_data: dict = self._account_api.ping(access_token=access_token)

            return SessionInfo(
                user_id=session_data["user_id"],
                access_token=access_token,
            )

        except WebTritErrorException as error:
            faultcode = extract_fault_code(error)
            if faultcode in ("Client.Session.ping.failed_to_process_access_token",):
                raise WebTritErrorException(
                    status_code=401,
                    # code = APIAccessErrorCode.authorization_header_missing,
                    error_message=f"Invalid access token {access_token}",
                )

            raise error

    def refresh_session(self, refresh_token: str) -> SessionInfo:
        """Refreshes the PortaSwitch account session.

        Parameters:
            :refresh_token (str): The token used to refresh the session.

        Returns:
            :(SessionInfo): The object with the obtained session tokens.

        """
        try:
            session_data: dict = self._account_api.refresh(refresh_token=refresh_token)
            access_token: str = session_data["access_token"]
            account_info: dict = self._account_api.get_account_info(access_token=access_token)["account_info"]

            return SessionInfo(
                user_id=account_info["i_account"],
                access_token=session_data["access_token"],
                refresh_token=session_data["refresh_token"],
                expires_at=datetime.now() + timedelta(seconds=session_data["expires_in"]),
            )

        except WebTritErrorException as error:
            faultcode = extract_fault_code(error)
            if faultcode in (
                "Server.Session.refresh_access_token.refresh_failed",
                "Client.Session.check_auth.failed_to_process_access_token",
            ):
                raise WebTritErrorException(
                    status_code=404,
                    # code = SessionNotFoundCode.session_not_found,
                    error_message=f"Invalid refresh token {refresh_token}",
                )

            raise error

    def close_session(self, access_token: str) -> bool:
        """Closes the PortaSwitch account session.

        Parameters:
            :access_token (str): The token used to close the session.

        Returns:
            :(bool): Shows whether is succeeded to close the session.

        """
        try:
            return self._account_api.logout(access_token=access_token)["success"] == 1

        except WebTritErrorException as error:
            faultcode = extract_fault_code(error)
            if faultcode in ("Client.Session.logout.failed_to_process_access_token",):
                raise WebTritErrorException(
                    status_code=404,
                    # code = UserAccessErrorCode.session_not_found,
                    error_message=f"Error closing the session {access_token}",
                )

            raise error

    def retrieve_user(self, session: SessionInfo, user: UserInfo) -> EndUser:
        """Returns information about the PortaSwitch account in WebTrit representation.

        Parameters:
            :session (SessionInfo): The session of the PortaSwitch account.
            :user (UserInfo): The information about the PortaSwitch account.

        Returns:
            :(EndUser): Fetched information about the PortaSwitch account in WebTrit representation.

        """
        try:
            account_info: dict = self._account_api.get_account_info(
                access_token=safely_extract_scalar_value(session.access_token)
            )["account_info"]

            aliases: list = self._account_api.get_alias_list(
                access_token=safely_extract_scalar_value(session.access_token)
            )["alias_list"]

            return Serializer.get_end_user(
                account_info,
                aliases,
                self._sip_server,
                self._portaswitch_settings.HIDE_BALANCE_IN_USER_INFO,
                self._settings.JANUS_SIP_FORCE_TCP,
            )

        except WebTritErrorException as error:
            faultcode = extract_fault_code(error)
            if faultcode in ("Client.Session.check_auth.failed_to_process_access_token",):
                # Race condition case, when session is validated and then the access_token dies.
                raise WebTritErrorException(
                    status_code=404,
                    # code = UserAccessErrorCode.session_not_found,
                    error_message="User not found",
                )

            raise error

    def retrieve_contacts(self, session: SessionInfo, user: UserInfo) -> list[ContactInfo]:
        """Returns information about other extentions of the same PortaSwitch customer.

        Parameters:
            :session (SessionInfo): The session of the PortaSwitch account.
            :user (UserInfo): The information about the PortaSwitch account.

        Returns:
            :(list[ContactInfo]): Fetched information about other extentions of the same PortaSwitch
                customer in the WebTrit representation.

        """
        try:
            account_info = self._account_api.get_account_info(safely_extract_scalar_value(session.access_token))[
                "account_info"
            ]
            i_customer = int(account_info["i_customer"])
            i_account = int(account_info["i_account"])

            match self._portaswitch_settings.CONTACTS_SELECTING:
                case PortaSwitchContactsSelectingMode.EXTENSIONS:
                    accounts = self._admin_api.get_account_list(i_customer)["account_list"]
                    account_to_aliases = {account["i_account"]: account.get("alias_list", []) for account in accounts}
                    extensions = self._admin_api.get_extensions_list(i_customer)["extensions_list"]

                    return [
                        Serializer.get_contact_info_by_extension(
                            ext, account_to_aliases.get(ext.get("i_account"), []), i_account
                        )
                        for ext in extensions
                        if ext["type"] in self._portaswitch_settings.CONTACTS_SELECTING_EXTENSION_TYPES
                    ]
                case PortaSwitchContactsSelectingMode.ACCOUNTS:
                    accounts = self._admin_api.get_account_list(i_customer)["account_list"]

                    contacts = []
                    for account in accounts:
                        dual_version_system = PortaSwitchDualVersionSystem(account.get("dual_version_system"))
                        if dual_version_system != PortaSwitchDualVersionSystem.SOURCE:
                            if not self._portaswitch_settings.CONTACTS_SKIP_WITHOUT_EXTENSION or account.get(
                                "extension_id"
                            ):
                                contacts.append(Serializer.get_contact_info_by_account(account, i_account))

                    return contacts

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Client.Session.check_auth.failed_to_process_access_token",):
                # Race condition case, when session is validated and then the access_token dies.
                raise WebTritErrorException(
                    status_code=404,
                    # code = UserAccessErrorCode.session_not_found,
                    error_message="User not found",
                )

            raise error

    def retrieve_calls(
        self,
        session: SessionInfo,
        user: UserInfo,
        page: int,
        items_per_page: int,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
    ) -> tuple[list[CDRInfo], int]:
        """Returns the CDR history of the logged in PortaSwitch account.

        Parameters:
            :session (SessionInfo): The session of the PortaSwitch account.
            :user (UserInfo): The information about the PortaSwitch account.
            :page (int): Shows what page of the CDR history to return.
            :items_per_page (int): Shows the number of items to return.
            :time_from (datetime|None): Filters the time frame of the CDR history.
            :time_to (datetime|None): Filters the time frame of the CDR history.

        Returns:
            :(tuple[list[CDRInfo], int]): Fetched CDR history and the number of total records
                that are located in the DB without taking into account the pagination.

        """
        try:
            time_from: datetime = time_from if time_from else datetime(1970, 1, 1)
            time_to: datetime = time_to if time_to else datetime(9000, 1, 1)

            result: dict = self._account_api.get_xdr_list(
                access_token=safely_extract_scalar_value(session.access_token),
                page=page,
                items_per_page=items_per_page,
                time_from=time_from,
                time_to=time_to,
            )

            return ([Serializer.get_cdr_info(cdr) for cdr in result["xdr_list"]], result["total"])

        except WebTritErrorException as error:
            faultcode = extract_fault_code(error)
            if faultcode in ("Client.Session.check_auth.failed_to_process_access_token",):
                # Race condition case, when session is validated and then the access_token dies.
                raise WebTritErrorException(
                    status_code=404,
                    # code = UserNotFoundCode.user_not_found,
                    error_message="User not found",
                )

            raise error

    def retrieve_call_recording(self, session: SessionInfo, call_recording: CallRecordingId) -> bytes:
        """Returns the binary representation of the recorded call.

        Parameters:
            :session (SessionInfo): The session of the PortaSwitch account.
            :call_recording (CallRecordingId): Contains an identifier of a call recording record.

        Returns:
            :(bytes): Raw bytes of a call recording file.

        """
        try:
            recording_id = safely_extract_scalar_value(call_recording)

            return self._account_api.get_call_recording(
                access_token=safely_extract_scalar_value(session.access_token), recording_id=recording_id
            )

        except WebTritErrorException as error:
            faultcode = extract_fault_code(error)
            if faultcode in ("Server.CDR.xdr_not_found",):
                # Race condition case, when session is validated and then the access_token dies.
                raise WebTritErrorException(
                    status_code=404,
                    # code = UserAccessErrorCode.session_not_found,
                    error_message="The recording with such a recording_id is not found.",
                )

            raise error

    def retrieve_voicemails(self, session: SessionInfo, user: UserInfo) -> UserVoicemailsResponse:
        """Returns users voicemail messages
        Parameters:
            session :SessionInfo: The session of the PortaSwitch account.
            user :UserInfo: The information about the PortaSwitch account.

        Returns:
            EndUser: Filled structure of the UserVoicemailResponse.
        """
        try:
            mailbox_messages = self._account_api.get_mailbox_messages(
                safely_extract_scalar_value(session.access_token)
            )
            voicemail_messages = [Serializer.get_voicemail_message(message) for message in mailbox_messages]

            return UserVoicemailsResponse(
                messages=voicemail_messages, has_new_messages=any(not message.seen for message in voicemail_messages)
            )

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Client.Session.check_auth.failed_to_process_access_token",):
                raise WebTritErrorException(status_code=404, error_message="User not found")

            raise error

    def retrieve_voicemail_message_details(
        self, session: SessionInfo, user: UserInfo, message_id: str
    ) -> VoicemailMessageDetails:
        """Returns users voicemail message detail
        Parameters:
            session :SessionInfo: The session of the PortaSwitch account.
            user :UserInfo: The information about the PortaSwitch account.
            message_id :str: The unique ID of the voicemail message.

        Returns:
            EndUser: Filled structure of the VoicemailMessageDetails.
        """
        try:
            message_details = self._account_api.get_mailbox_message_details(
                safely_extract_scalar_value(session.access_token), message_id
            )

            return Serializer.get_voicemail_message_details(message_details)

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Client.Session.check_auth.failed_to_process_access_token",):
                raise WebTritErrorException(status_code=404, error_message="User not found")

            raise error

    def retrieve_voicemail_message_attachment(
        self, session: SessionInfo, message_id: str, file_format: str
    ) -> Iterator:
        """Returns the binary representation for attachent of the voicemail message.

        Parameters:
            session :SessionInfo: The session of the PortaSwitch account.
            message_id :str: The unique ID of the voicemail message.
            file_format :PortaSwitchMailboxMessageAttachmentFormat: Provided file format.

        Returns:
            :bytes: Raw bytes of a message attachment.
        """

        file_format = file_format and file_format.lower()
        if file_format and not PortaSwitchMailboxMessageAttachmentFormat.has_value(file_format):
            raise WebTritErrorException(422, "Not supported file format", code="unsupported_file_format")

        try:
            return self._account_api.get_mailbox_message_attachment(
                safely_extract_scalar_value(session.access_token),
                message_id,
                file_format or PortaSwitchMailboxMessageAttachmentFormat.WAV.value,
            )

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Client.Session.check_auth.failed_to_process_access_token",):
                raise WebTritErrorException(404, "User not found")

            raise error

    def patch_voicemail_message(
        self, session: SessionInfo, message_id: str, body: UserVoicemailMessagePatch
    ) -> UserVoicemailMessagePatch:
        """Update attributes for a user's voicebox message.

        Parameters:
            session :SessionInfo: The session of the PortaSwitch account.
            message_id :str: The unique ID of the voicemail message.
            body: :bool: Attributes to patch.

        Returns:
            Response :UserVoicemailMessageSeenResponse: Filled structure of the UserVoicemailMessageSeenResponse.
        """
        seen = body.seen

        try:
            self._account_api.set_mailbox_message_flag(
                safely_extract_scalar_value(session.access_token),
                message_id,
                PortaSwitchMailboxMessageFlag.SEEN,
                PortaSwitchMailboxMessageFlagAction.SET if seen else PortaSwitchMailboxMessageFlagAction.UNSET,
            )

            return UserVoicemailMessagePatch(seen=seen)

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Client.Session.check_auth.failed_to_process_access_token",):
                raise WebTritErrorException(status_code=404, error_message="User not found")

            raise error

    def delete_voicemail_message(self, session: SessionInfo, message_id: str) -> None:
        """Delete an existing user's voicebox message.
        Parameters:
            session :SessionInfo: The session of the PortaSwitch account.
            message_id :str: The unique ID of the voicemail message.
        """
        try:
            self._account_api.delete_mailbox_message(safely_extract_scalar_value(session.access_token), message_id)

        except WebTritErrorException as error:
            fault_code = extract_fault_code(error)
            if fault_code in ("Client.Session.check_auth.failed_to_process_access_token",):
                raise WebTritErrorException(status_code=404, error_message="User not found")

            raise error

    def create_new_user(self, user_data, tenant_id: str = None):
        """Create a new user as a part of the sign-up process - not supported yet"""
        raise NotImplementedError()

    def signup(self, user_data, tenant_id: str = None) -> UserCreateResponse:
        """Create a new user as a part of the sign-up process - not supported yet"""
        raise NotImplementedError()

    def custom_method_public(
        self,
        method_name: str,
        data: CustomRequest,
        headers: Optional[Dict] = None,
        tenant_id: str = None,
        lang: str = None,
    ) -> CustomResponse:
        attr_name = method_name.replace("-", "_")
        if method := getattr(self, attr_name, None):
            logging.debug(f"Processing custom public method {method_name} with {data} request")

            return method(data=data)
        else:
            raise WebTritErrorException(
                status_code=404, error_message=f"Method '{method_name}' not found", code="method_not_found"
            )

    def custom_method_private(
        self,
        session: SessionInfo,
        user_id: str,
        method_name: str,
        data: CustomRequest,
        headers: Optional[Dict] = None,
        tenant_id: str = None,
        lang: str = None,
    ) -> CustomResponse:
        attr_name = f"_{method_name.replace('-', '_')}"
        if method := getattr(self, attr_name, None):
            logging.debug(f"Processing custom private method {method_name} from user {user_id} with {data} request")

            return method(user_id=user_id, data=data)
        else:
            raise WebTritErrorException(
                status_code=404, error_message=f"Method '{method_name}' not found", code="method_not_found"
            )

    def submit_user_sip_registration_status(self, session: SessionInfo, user: UserInfo, status: SIPRegistrationStatus, timestamp: datetime, reason: Optional[str] = None) -> None:
        """Submit user's SIP registration status"""
        raise NotImplementedError()

    # region custom methods handlers

    def _self_config_portal_url(self, user_id: str, data: CustomRequest) -> CustomResponse:
        account_info = self._admin_api.get_account_info(i_account=user_id).get("account_info")
        session_data = self._account_api.login(account_info["login"], account_info["password"])

        return CustomResponse(
            url=f"{self._settings.SELF_CONFIG_PORTAL_URL}?token={session_data['access_token']}",
            expires_at=datetime.now(UTC) + timedelta(seconds=session_data["expires_in"]),
        )

    # endregion
