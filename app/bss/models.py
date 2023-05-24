# generated by fastapi-codegen:
#   filename:  .\WebTrit-webtrit_adapter-1.0.5-resolved.json
#   timestamp: 2023-04-30T08:13:09+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, conint


class Detail(BaseModel):
    path: Optional[str] = None
    reason: Optional[str] = None


class ErrorResponse(BaseModel):
    code: str = Field(..., description='Unique error code identifier.')
    details: Optional[List[Union[Detail, Dict[str, Any]]]] = Field(
        None,
        description='Additional details related to the error code, which depend on the specific error.\n',
    )
    message: Optional[str] = Field(None, description='Description of the error.')


class Code(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserInfoUnauthorizedErrorResponse(ErrorResponse):
    code: Optional[Code] = None


class Code1(Enum):
    validation_error = 'validation_error'


class GetUserInfoUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code1] = None


class Code2(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserInfoNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code2] = None


class Code3(Enum):
    validation_error = 'validation_error'
    refresh_token_invalid = 'refresh_token_invalid'
    refresh_token_expired = 'refresh_token_expired'
    unknown = 'unknown'


class UpdateSessionUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code3] = None


class Code4(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserContactListNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code4] = None


class Code5(Enum):
    otp_id_not_found = 'otp_id_not_found'


class VerifySessionOtpNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code5] = None


class Code6(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserHistoryListUnauthorizedErrorResponse(ErrorResponse):
    code: Optional[Code6] = None


class RefreshToken(BaseModel):
    __root__: str = Field(
        ...,
        description='A single-use token for refreshing the API session and obtaining a new `access_token`.\n\nWhen the current `access_token` is close to expiration or has already expired, the\n`refresh_token` can be exchanged for a new `access_token`, ensuring uninterrupted access\nto the API without requiring the user to manually sign in again.\n\nPlease note that each `refresh_token` can only be used once, and a new `refresh_token`\nwill be issued along with the new `access_token`.\n',
        title='RefreshToken',
    )


class BinaryResponse(BaseModel):
    __root__: bytes = Field(..., title='BinaryResponse')


class UserId(BaseModel):
    __root__: str = Field(
        ...,
        description='A primary unique identifier of the user on the **Adaptee**.\n\nThis identifier is crucial for the proper functioning of **WebTrit Core**, as it is used\nto store information such as push tokens and other relevant data associated to the user.\n\nThe **Adaptee** must consistently return the same `UserId` for the same user,\nregardless of the `UserRef` used for sign-in.\n',
        example='123456789abcdef0123456789abcdef0',
        title='UserId',
    )


class Code7(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserContactListUnauthorizedErrorResponse(ErrorResponse):
    code: Optional[Code7] = None


class Status(Enum):
    unknown = 'unknown'
    registered = 'registered'
    notregistered = 'notregistered'


class SipStatus(BaseModel):
    display_name: str = Field(
        ...,
        description="The user's display name for SIP calls.",
        example='Annabelle Black',
    )
    status: Status = Field(
        ...,
        description='The current registration status of the user on the SIP server.',
    )


class Code8(Enum):
    validation_error = 'validation_error'
    delivery_channel_unspecified = 'delivery_channel_unspecified'
    signup_limit_reached = 'signup_limit_reached'


class CreateSessionOtpUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code8] = None


class Code9(Enum):
    invalid_credentials = 'invalid_credentials'


class CreateSessionUnauthorizedErrorResponse(ErrorResponse):
    code: Optional[Code9] = None


class Code10(Enum):
    external_api_issue = 'external_api_issue'


class GetUserHistoryListInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code10] = None


class UserRef(BaseModel):
    __root__: str = Field(
        ...,
        description='A reference identifier of the user on the **Adaptee**\n\nThis identifier is entered by the user in client applications and passed\nvia **WebTrit Core** to the **Adaptee** for sign-in purposes.\n\nThe identifier can be a phone number or any other attribute associated\nwith the user. When the same user is accessed using different references,\nit is crucial to ensure that the same `UserId` is assigned to this user.\n',
        example='1234567890',
        title='UserRef',
    )


class Code11(Enum):
    session_not_found = 'session_not_found'


class DeleteSessionNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code11] = None


class Code12(Enum):
    external_api_issue = 'external_api_issue'


class GetSystemInfoInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code12] = None


class SessionOtpCreateRequest(BaseModel):
    user_ref: UserRef


class SessionCreateRequest(BaseModel):
    login: str = Field(
        ..., description="User's `login` on the hosted PBX system / BSS."
    )
    password: str = Field(
        ..., description="User's `password` on the hosted PBX system / BSS."
    )


class SessionResponse(BaseModel):
    access_token: str = Field(
        ...,
        description='The `access_token` to be used in subsequent API\nrequests on behalf of the `user` (by default it is\nplaced in the bearer auth HTTP header).\n',
    )
    refresh_token: Optional[RefreshToken] = None
    user_id: UserId


class Code13(Enum):
    validation_error = 'validation_error'


class GetUserRecordingUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code13] = None


class Code14(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserHistoryListNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code14] = None


class Code15(Enum):
    external_api_issue = 'external_api_issue'


class CreateUserInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code15] = None


class SipServer(BaseModel):
    force_tcp: Optional[bool] = Field(
        None,
        description='If set to true, forces the use of TCP for SIP messaging.',
        example=False,
    )
    host: str = Field(
        ...,
        description='The SIP server address, which can be either a hostname or an IP address.',
        example='sip.webtrit.com',
    )
    port: Optional[int] = Field(
        None,
        description='The port on which the SIP server listens for incoming requests.',
        example=5060,
    )


class BalanceType(Enum):
    unknown = 'unknown'
    inapplicable = 'inapplicable'
    prepaid = 'prepaid'
    postpaid = 'postpaid'


class Balance(BaseModel):
    amount: Optional[float] = Field(
        None, description="The user's current balance.", example=50
    )
    balance_type: Optional[BalanceType] = Field(
        None,
        description='Meaning of the balance figure for this user.\n\n* `inapplicable` means the **Adaptee** does not handle\n  billing and does not have the balance data.\n* `prepaid` means the number reflects the funds that\n  the user has available for spending.\n* `postpaid` means the balance reflects the amount of\n  previously accumulated charges (how much the user\n  owes - to be used in conjunction with a `credit_limit`).\n',
    )
    credit_limit: Optional[float] = Field(
        None, description="The user's credit limit (if applicable).", example=100
    )
    currency: Optional[str] = Field(
        '$',
        description='Currency symbol or name in ISO 4217:2015 format (e.g. USD).',
        example='$',
    )


class Code16(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserRecordingNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code16] = None


class Code17(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserRecordingUnauthorizedErrorResponse(ErrorResponse):
    code: Optional[Code17] = None


class Code18(Enum):
    external_api_issue = 'external_api_issue'


class CreateSessionOtpInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code18] = None


class SipInfo(BaseModel):
    display_name: Optional[str] = Field(
        None,
        description="The visible identification of the caller to be included in the SIP request.\nThis will be shown to the called party as the caller's name. If not provided,\nthe `display_name` will be populated with the `login`.\n",
        example='Thomas A. Anderson',
    )
    login: str = Field(
        ...,
        description='The username to be used in SIP requests.',
        example='14155551234',
    )
    password: str = Field(
        ..., description='The password for the SIP account.', example='strong_password'
    )
    registration_server: Optional[SipServer] = None
    sip_server: SipServer


class Code19(Enum):
    external_api_issue = 'external_api_issue'


class GetUserContactListInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code19] = None


class Code20(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class DeleteSessionUnauthorizedErrorResponse(ErrorResponse):
    code: Optional[Code20] = None


class Code21(Enum):
    validation_error = 'validation_error'


class GetUserContactListUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code21] = None


class Code22(Enum):
    external_api_issue = 'external_api_issue'


class CreateSessionInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code22] = None


class Code23(Enum):
    external_api_issue = 'external_api_issue'


class DeleteSessionInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code23] = None


class Code24(Enum):
    external_api_issue = 'external_api_issue'


class UpdateSessionInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code24] = None


class Code25(Enum):
    external_api_issue = 'external_api_issue'


class VerifySessionOtpInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code25] = None


class SessionUpdateRequest(BaseModel):
    refresh_token: RefreshToken


class Code26(Enum):
    signup_disabled = 'signup_disabled'


class CreateSessionOtpMethodNotAllowedErrorResponse(ErrorResponse):
    code: Optional[Code26] = None


class DeliveryChannel(Enum):
    email = 'email'
    sms = 'sms'
    call = 'call'
    other = 'other'


class Code27(Enum):
    validation_error = 'validation_error'
    otp_id_verified = 'otp_id_verified'
    otp_id_verification_attempts_exceeded = 'otp_id_verification_attempts_exceeded'
    otp_id_timeout = 'otp_id_timeout'
    code_incorrect = 'code_incorrect'


class VerifySessionOtpUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code27] = None


class Direction(Enum):
    incoming = 'incoming'
    outgoing = 'outgoing'


class ConnectStatus(Enum):
    accepted = 'accepted'
    declined = 'declined'
    missed = 'missed'
    error = 'error'


class Code28(Enum):
    validation_error = 'validation_error'
    signup_limit_reached = 'signup_limit_reached'


class CreateUserUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code28] = None


class UserCreateRequest(BaseModel):
    pass


class Code29(Enum):
    session_not_found = 'session_not_found'


class UpdateSessionNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code29] = None


class Code30(Enum):
    external_api_issue = 'external_api_issue'


class GetUserInfoInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code30] = None


class SupportedEnum(Enum):
    signup = 'signup'
    otpSignin = 'otpSignin'
    passwordSignin = 'passwordSignin'
    recordings = 'recordings'
    callHistory = 'callHistory'
    extensions = 'extensions'


class GeneralSystemInfoResponse(BaseModel):
    custom: Optional[Dict[str, str]] = Field(
        None,
        description='Additional custom key-value pairs providing extended information about\nthe **Adaptee** and/or its environment.\n',
    )
    name: str
    supported: List[SupportedEnum] = Field(
        ...,
        description='A list of supported functionalities by the **Adaptee**.\n\nPossible functionalities values:\n* `signup` - supports the creation of new customer accounts\n* `otpSignin` - allows user authorization via One-Time Password (OTP)\n* `passwordSignin` - allows user authorization using login and password\n* `recordings` - provides access to call recordings\n* `callHistory` - provides access to call history\n* `extensions` - retrieves the list of other users (contacts)\n',
    )
    version: str


class Code31(Enum):
    signup_disabled = 'signup_disabled'


class CreateUserMethodNotAllowedErrorResponse(ErrorResponse):
    code: Optional[Code31] = None


class OtpId(BaseModel):
    __root__: str = Field(
        ...,
        description='Unique identifier of the OTP request on the **Adapter** and/or **Adaptee** side.\n\nNote: This ID is NOT the code that the user will enter. It serves\nto match the originally generated OTP with the one provided by the user.\n',
        example='12345678-9abc-def0-1234-56789abcdef0',
        title='OtpId',
    )


class CallRecordingId(BaseModel):
    __root__: str = Field(
        ...,
        description='A unique identifier for a call recording, used to reference the recorded media of a specific call.\n',
        title='CallRecordingId',
    )


class Code32(Enum):
    validation_error = 'validation_error'


class CreateSessionUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code32] = None


class Code33(Enum):
    external_api_issue = 'external_api_issue'


class GetUserRecordingInternalServerErrorErrorResponse(ErrorResponse):
    code: Optional[Code33] = None


class Code34(Enum):
    validation_error = 'validation_error'


class GetUserHistoryListUnprocessableEntityErrorResponse(ErrorResponse):
    code: Optional[Code34] = None


class Numbers(BaseModel):
    additional: Optional[List[str]] = Field(
        None,
        description='A list of other phone numbers associated with the user. This may\ninclude extra phone numbers that the user purchased (also called\ndirect-inward-dials or DID) to ring on their VoIP phone,\nand other numbers that can be used to identify them in the\naddress book of others (e.g. their mobile number).\n',
        example=['380441234567', '34911234567'],
    )
    ext: Optional[str] = Field(
        None,
        description="The user's extension number (short dialing code) within the **Adaptee**.\n",
        example='0001',
    )
    main: str = Field(
        ...,
        description="The user's primary phone number. It is strongly suggested\nto use the full number, including the country code\n(also known as the E.164 format).\n",
        example='14155551234',
    )


class Code35(Enum):
    user_not_found = 'user_not_found'


class CreateSessionOtpNotFoundErrorResponse(ErrorResponse):
    code: Optional[Code35] = None


class Code36(Enum):
    invalid_credentials = 'invalid_credentials'


class CreateSessionUnauthorizedErrorResponse1(ErrorResponse):
    code: Optional[Code36] = None


class Code37(Enum):
    validation_error = 'validation_error'


class CreateSessionUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code37] = None


class Code38(Enum):
    external_api_issue = 'external_api_issue'


class CreateSessionInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code38] = None


class Code39(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class DeleteSessionUnauthorizedErrorResponse1(ErrorResponse):
    code: Optional[Code39] = None


class Code40(Enum):
    session_not_found = 'session_not_found'


class DeleteSessionNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code40] = None


class Code41(Enum):
    external_api_issue = 'external_api_issue'


class DeleteSessionInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code41] = None


class Code42(Enum):
    session_not_found = 'session_not_found'


class UpdateSessionNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code42] = None


class Code43(Enum):
    validation_error = 'validation_error'
    refresh_token_invalid = 'refresh_token_invalid'
    refresh_token_expired = 'refresh_token_expired'
    unknown = 'unknown'


class UpdateSessionUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code43] = None


class Code44(Enum):
    external_api_issue = 'external_api_issue'


class UpdateSessionInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code44] = None


class Code45(Enum):
    user_not_found = 'user_not_found'


class CreateSessionOtpNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code45] = None


class Code46(Enum):
    signup_disabled = 'signup_disabled'


class CreateSessionOtpMethodNotAllowedErrorResponse1(ErrorResponse):
    code: Optional[Code46] = None


class Code47(Enum):
    validation_error = 'validation_error'
    delivery_channel_unspecified = 'delivery_channel_unspecified'
    signup_limit_reached = 'signup_limit_reached'


class CreateSessionOtpUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code47] = None


class Code48(Enum):
    external_api_issue = 'external_api_issue'


class CreateSessionOtpInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code48] = None


class Code49(Enum):
    otp_id_not_found = 'otp_id_not_found'


class VerifySessionOtpNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code49] = None


class Code50(Enum):
    validation_error = 'validation_error'
    otp_id_verified = 'otp_id_verified'
    otp_id_verification_attempts_exceeded = 'otp_id_verification_attempts_exceeded'
    otp_id_timeout = 'otp_id_timeout'
    code_incorrect = 'code_incorrect'


class VerifySessionOtpUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code50] = None


class Code51(Enum):
    external_api_issue = 'external_api_issue'


class VerifySessionOtpInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code51] = None


class Code52(Enum):
    external_api_issue = 'external_api_issue'


class GetSystemInfoInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code52] = None


class Code53(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserInfoUnauthorizedErrorResponse1(ErrorResponse):
    code: Optional[Code53] = None


class Code54(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserInfoNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code54] = None


class Code55(Enum):
    validation_error = 'validation_error'


class GetUserInfoUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code55] = None


class Code56(Enum):
    external_api_issue = 'external_api_issue'


class GetUserInfoInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code56] = None


class Code57(Enum):
    signup_disabled = 'signup_disabled'


class CreateUserMethodNotAllowedErrorResponse1(ErrorResponse):
    code: Optional[Code57] = None


class Code58(Enum):
    validation_error = 'validation_error'
    signup_limit_reached = 'signup_limit_reached'


class CreateUserUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code58] = None


class Code59(Enum):
    external_api_issue = 'external_api_issue'


class CreateUserInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code59] = None


class Code60(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserContactListUnauthorizedErrorResponse1(ErrorResponse):
    code: Optional[Code60] = None


class Code61(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserContactListNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code61] = None


class Code62(Enum):
    validation_error = 'validation_error'


class GetUserContactListUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code62] = None


class Code63(Enum):
    external_api_issue = 'external_api_issue'


class GetUserContactListInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code63] = None


class Code64(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserHistoryListUnauthorizedErrorResponse1(ErrorResponse):
    code: Optional[Code64] = None


class Code65(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserHistoryListNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code65] = None


class Code66(Enum):
    validation_error = 'validation_error'


class GetUserHistoryListUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code66] = None


class Code67(Enum):
    external_api_issue = 'external_api_issue'


class GetUserHistoryListInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code67] = None


class Code68(Enum):
    authorization_header_missing = 'authorization_header_missing'
    bearer_credentials_missing = 'bearer_credentials_missing'
    access_token_invalid = 'access_token_invalid'
    access_token_expired = 'access_token_expired'
    unknown = 'unknown'


class GetUserRecordingUnauthorizedErrorResponse1(ErrorResponse):
    code: Optional[Code68] = None


class Code69(Enum):
    session_not_found = 'session_not_found'
    user_not_found = 'user_not_found'


class GetUserRecordingNotFoundErrorResponse1(ErrorResponse):
    code: Optional[Code69] = None


class Code70(Enum):
    validation_error = 'validation_error'


class GetUserRecordingUnprocessableEntityErrorResponse1(ErrorResponse):
    code: Optional[Code70] = None


class Code71(Enum):
    external_api_issue = 'external_api_issue'


class GetUserRecordingInternalServerErrorErrorResponse1(ErrorResponse):
    code: Optional[Code71] = None


class UserHistoryIndexResponsePagination(BaseModel):
    items_per_page: Optional[conint(ge=1)] = Field(
        None, description='Number of items per page.', example=100
    )
    items_total: Optional[conint(ge=1)] = Field(
        None,
        description='Total number of CDRs within the selected time period\nor within the entire history if no time period is provided.\n',
        example=1000,
    )
    page: Optional[conint(ge=1)] = Field(
        None, description='Current page number.', example=1
    )


class SessionOtpVerifyRequest(BaseModel):
    code: str = Field(
        ...,
        description='Code (one-time-password) that the end-user receives from\nthe hosted PBX system or BSS via email/SMS and then uses in\napplication to confirm his/her identity and login.\n',
    )
    otp_id: OtpId


class Contact(BaseModel):
    company_name: Optional[str] = Field(
        None,
        description='The name of the company the user is associated with.',
        example='Matrix',
    )
    email: Optional[EmailStr] = Field(
        None, description="The user's email address.", example='a.black@matrix.com'
    )
    first_name: Optional[str] = Field(
        None, description="The user's first name.", example='Annabelle'
    )
    last_name: Optional[str] = Field(
        None, description="The user's last name.", example='Black'
    )
    numbers: Optional[Numbers] = None
    sip: Optional[SipStatus] = None

class UserStatus(Enum):
    active = 'active'
    limited = 'limited'
    blocked = 'blocked'

class UserInfoShowResponse(BaseModel):
    balance: Optional[Balance] = None
    company_name: Optional[str] = Field(
        None, description='The company the user is associated with.', example='Matrix'
    )
    email: Optional[EmailStr] = Field(
        None, description="The user's email address.", example='neo@matrix.com'
    )
    first_name: Optional[str] = Field(
        None, description="The user's first name.", example='Thomas'
    )
    last_name: Optional[str] = Field(
        None, description="The user's last name.", example='Anderson'
    )
    status: Optional[UserStatus] = Field(
        description="Whether this user is active or blocked", example='active',
        default_factory=UserStatus.active
    )
    numbers: Optional[Numbers] = None
    sip: SipInfo
    time_zone: Optional[str] = Field(
        None,
        description="The preferred time zone for the user's displayed time values\n(see [time zones list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)).\nIf not provided, the **WebTrit Core** server time zone is used.\n",
        example='Europe/Kyiv',
    )


class UserContactIndexResponse(BaseModel):
    items: Optional[List[Contact]] = None


class SessionOtpCreateResponse(BaseModel):
    delivery_channel: Optional[DeliveryChannel] = Field(
        None,
        description='Specifies the channel used to deliver the OTP to the user\n(e.g., email, SMS, call, or other). This information helps guide the\nuser on where to find the OTP.\n',
    )
    delivery_from: Optional[str] = Field(
        None,
        description='Identifies the sender of the OTP, making it easier for the user to\nlocate the correct message. Depending on the `delivery_channel`, this\nvalue may be an email address, phone number, or a description of an\nalternative method. In the case of email, if the message is marked as\nspam, the user can add this address to a whitelist for future\nreference.\n',
    )
    otp_id: OtpId


class CDRInfo(BaseModel):
    callee: str = Field(
        ...,
        description='The phone number of the called party (recipient of the call, CLD).',
        example='14155551234',
    )
    caller: str = Field(
        ...,
        description='The phone number of the calling party (originator of the call, CLI).',
        example='0001',
    )
    connect_time: Optional[datetime] = Field(
        None,
        description='Datetime of the call connection in ISO format.',
        example='2023-01-01T09:00:00Z',
    )
    direction: Direction = Field(..., description='Indicates the call direction.')
    disconnected_reason: Optional[str] = Field(
        None,
        description='Describes the reason for the call disconnection.',
        example='Caller hangup',
    )
    duration: Optional[int] = Field(
        None, description='Call duration (in seconds), 0 for failed calls.', example=60
    )
    recording_id: Optional[CallRecordingId] = None
    status: ConnectStatus = Field(..., description='Indicates the call status.')


class UserCreateResponse(BaseModel):
    __root__: Union[Dict[str, Any], SessionOtpCreateResponse, SessionResponse] = Field(
        ..., title='UserCreateResponse'
    )


class UserHistoryIndexResponse(BaseModel):
    items: Optional[List[CDRInfo]] = None
    pagination: Optional[UserHistoryIndexResponsePagination] = None
