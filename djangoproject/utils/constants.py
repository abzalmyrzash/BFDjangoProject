USER_ROLE_SUPER_ADMIN = 1
USER_ROLE_GUEST = 2
USER_ROLES = (
    (USER_ROLE_SUPER_ADMIN, 'super admin'),
    (USER_ROLE_GUEST, 'guest'),
)

REQUEST_STATUS_PENDING = 0
REQUEST_STATUS_ACCEPTED = 1
REQUEST_STATUS_DECLINED = 2
REQUEST_STATUS = (
    (REQUEST_STATUS_PENDING, 'pending'),
    (REQUEST_STATUS_ACCEPTED, 'accepted'),
    (REQUEST_STATUS_DECLINED, 'declined'),
)

REACTION_TYPE_LIKE = 1
REACTION_TYPE_FUNNY = 2
REACTION_TYPE_WOW = 3
REACTION_TYPE_SAD = 4
REACTION_TYPE_ANGRY = 5
REACTION_TYPE_TROLL = 666
REACTION_TYPES = (
    (REACTION_TYPE_LIKE, 'Like it!'),
    (REACTION_TYPE_FUNNY, 'Haha!'),
    (REACTION_TYPE_WOW, 'Wow!'),
    (REACTION_TYPE_SAD, 'Sad :('),
    (REACTION_TYPE_ANGRY, 'Unacceptable!'),
    (REACTION_TYPE_TROLL, 'U mad bro?'),
)

GENDER_MALE = 1
GENDER_FEMALE = 2
GENDERS = (
    (GENDER_MALE, 'male'),
    (GENDER_FEMALE, 'female'),
)

MINIMUM_AGE = 13

# used to notify the user about reaction count
REACTION_COUNT_MILESTONES = [1, 5, 25, 100, 1000]
