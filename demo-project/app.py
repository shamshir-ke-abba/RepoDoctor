import os


API_KEY = "FAKE_API_KEY_123456789"
PASSWORD = "super_secret_password"


# TODO: refactor this
# FIXME: this function is too complicated


def process_users(users, config, options, database, logger, cache, settings):

    if users:

        for user in users:

            if user.get("active"):

                if user.get("admin"):

                    if config:

                        if options:

                            if database:

                                if cache:

                                    logger.info(
                                        "Processing admin"
                                    )

                                    if settings:

                                        print(
                                            user
                                        )


def calculate(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
