import logging

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis_om import NotFoundError
from starlette.requests import Request

from .entity import UserData

logger = logging.getLogger("rzbportal.security")


class Security:
    """Security class for handling user authentication and authorization.
    Attributes:
        raw_jwt (str): The raw JSON Web Token (JWT) for the user.
        user_data (UserData): The user data object containing user information and ACLs.
        id_token (str): The user ID token.
    """

    def __init__(
        self,
        raw_jwt: str,
        user_data: UserData,
        id_token: str
    ):
        self._raw_jwt = raw_jwt
        self._user_data: UserData = user_data
        self._id_token = id_token

    @property
    def raw_jwt(self) -> str:
        """
        Returns the raw JSON Web Token (JWT) as a string.
        Returns:
            str: The raw JWT.
        """

        return self._raw_jwt
    
    def can(self, acl: str) -> bool:
        """
        Check if the user has the specified access control level (ACL).
        Args:
            acl (str): The access control level to check.
        Returns:
            bool: True if the user has the specified ACL, False otherwise.
        """
        for user_acl in self._user_data.acl:
            if acl == user_acl:
                return True
        return False
    
    def can_all(self, acl_list: list[str]) -> bool:
        """
        Check if the user has all the specified access control levels (ACLs).
        Args:
            acl_list (list[str]): A list of access control levels to check.
        Returns:
            bool: True if the user has all the specified ACLs, False otherwise.
        """
        for acl in acl_list:
            if not self.can(acl):
                return False
        return True
    
    def can_any(self, acl_list: list[str]) -> bool:
        """
        Check if the user has any of the specified access control levels (ACLs).
        Args:
            acl_list (list[str]): A list of access control levels to check.
        Returns:
            bool: True if the user has any of the specified ACLs, False otherwise.
        """
        for acl in acl_list:
            if self.can(acl):
                return True
        return False

    @property
    def acl(self):
        """
        Retrieve the access control list (ACL) for the current user.
        Returns:
            list: A list representing the ACL of the user.
        """
        return self._user_data.acl
    
    @property
    def user_data(self) -> UserData:
        """
        Retrieve the user data object.
        Returns:
            UserData: The user data object.
        """
        return self._user_data
    
    @property
    def id_token(self) -> str:
        """
        Retrieve the user ID token.
        Returns:
            UUID: The user ID token.
        """
        return self._id_token


class SecurityProvider(HTTPBearer):
    def __init__(self, jwt_sercret_key: str):
        self._jwt_secret_key = jwt_sercret_key
        super(SecurityProvider, self).__init__(scheme_name="jwt", description="Your JWT token", auto_error=False)

    async def __call__(self, request: Request) -> Security:
        """
        Asynchronous call method to handle incoming requests and provide security validation.
        Args:
            request (Request): The incoming request object.
        Returns:
            Security: An instance of the Security class containing the raw JWT and user data.
        Raises:
            HTTPException: If no credentials are provided, if the JWT data is invalid, or if user info is not found.

        # Example usage of SecurityProvider in a FastAPI route
        app = FastAPI()
        security_provider = SecurityProvider(jwt_sercret_key="your_jwt_secret_key")

        @app.get("/protected-route")
        async def protected_route(security: Security = Depends(security_provider)):
            if not security.can("required_acl"):
            raise HTTPException(status_code=403, detail="Access forbidden")
            return {"message": "You have access to this route"}
        """

        credentials: HTTPAuthorizationCredentials | None = await super(SecurityProvider, self).__call__(request)

        if credentials is None:
            logger.error("No credentials provided")
            raise HTTPException(status_code=403, detail="Token is invalid")
        
        jwt_data: dict = jwt.decode(credentials.credentials, self._jwt_secret_key, algorithms=["HS256"])

        if not jwt_data.get('id_user'):
            logger.error("Invalid JWT data, please check content for id_user")
            raise HTTPException(status_code=403, detail="JWT data are invalid")
        
        data = UserData.get(jwt_data['id_user'])

        try:
            data = UserData.get(jwt_data['id_user'])
            return Security(
                raw_jwt=credentials.credentials,
                user_data=data,
                id_token=jwt_data['id_token']
            )
        except NotFoundError:
            logger.error("User info not found in redis")
            raise HTTPException(status_code=403, detail="User info not found, please login again")
        

