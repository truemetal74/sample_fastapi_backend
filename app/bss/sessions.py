from datetime import datetime, timedelta
from bss.dbs import FileStoredKeyValue
import logging
import uuid
from app_config import AppConfig
from bss.models import SessionApprovedResponseSchema

class SessionInfo(SessionApprovedResponseSchema):
    """Info about a session, initiated by WebTrit core on behalf of user"""

    def still_active(self, timestamp=datetime.now()) -> bool:
        """Check whether the session has not yet expired"""

        return self.expires_at > timestamp
    
class SessionStorage:
    """A class that provides access to stored session data (which can
    be stored in some SQL/no-SQL database, external REST services, etc.)"""

    def __init__(self, session_db):
        """Initialize the object using the provided object
        for storing the sessions"""
        self.session_db = session_db

    def __refresh_token_index(self, id: str) -> str:
        """Change the value of refresh token so it still will
        be unique, but cannot match any of the access tokens."""
        if hasattr(id, "__root__"):
            id = id.__root__
        return "R" + id

    def get_session(self, access_token="", refresh_token: str = None) -> SessionInfo:
        """Retrieve a session"""

        if refresh_token:
            refr_id = self.__refresh_token_index(refresh_token)
            return self.session_db.get(refr_id, None)
        return self.session_db.get(access_token, None)

    def create_session(self, user_id: str) -> SessionInfo:
        expiration = datetime.now() + timedelta(days=1) 
        expiration = expiration.replace(microsecond=0)
        session = SessionInfo(
            user_id=user_id,
            access_token=str(uuid.uuid1()),
            refresh_token=str(uuid.uuid1()),
            expires_at=expiration,
        )

        return session
    
    def __store_session(self, session: SessionInfo):
        self.session_db[session.access_token] = session
        # also add the possibility to find the session by its refresh token
        refresh_token = self.__refresh_token_index(session.refresh_token)
        self.session_db[refresh_token] = session

    def store_session(self, session: SessionInfo):
        """Store a session in the database"""
        self.__store_session(session)

    def __delete_session(self, access_token: str, refresh_token: str = None) -> bool:
        """Remove a session from the database"""

        if refresh_token:
            del self.session_db[refresh_token]
        session = self.session_db.pop(access_token, None)

        return True if session else False
    
    def delete_session(self, access_token: str, refresh_token: str = None) -> bool:
        """Remove a session from the database"""

        return self.__delete_session(access_token, refresh_token)


# class FileSessionStorage(SessionStorage):
#     """Store sessions in local file. Suitable only
#     for demo / development. Implement a real persistent & scalable
#     session storage for your application, or use a class like
#     FirestoreSessionStorage below."""
#     def __init__(self, config: AppConfig):
#         super().__init__(config)
#         # to make the sessions survive a restart of a container - 
#         # ensure that /var/db/ (or whichever
#         # location you choose) is mounted as a volume to the container
#         file_name = config.get_conf_val('Sessions', 'StorageFile',
#                             default = '/var/db/sessions.db')
#         logging.debug(f"Using file {file_name} for session storage")
#         self.sessions = FileStoredKeyValue(file_name)

