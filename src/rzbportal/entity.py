from redis_om import Field, JsonModel
from uuid import UUID

# THis file contains all entities that should be used across all microservices of
# the application. It is important to keep all entities in one place to avoid confusion.
# Please update this file with HIGHEST caution!
# WARNING, DANGER, WARNING!!! And i mean it!

class UserData(JsonModel):
    """
    UserData model representing user information that is stored in redis. Contains everything
    so it have to be used internally only!
    Attributes:
        id_user (UUID): Unique identifier for the user.
        public_name (str): Public name of the user.
        member_number (int): Membership number of the user.
        personal_data (dict): Dictionary containing personal data of the user.
        email (str): Email address of the user.
        acl (list): Access control list for the user.
    """

    id_user: UUID = Field(title="User ID", index=True, primary_key=True)
    public_name: str = Field(title="Public name")
    member_number: int = Field(title="Member number")
    personal_data: dict = Field(title="Personal data", default_factory=dict)
    email: str = Field(title="Email")
    acl: list = Field(title="Access control list", default_factory=list)