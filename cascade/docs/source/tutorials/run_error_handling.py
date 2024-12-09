from cascade.base import Config


class TestConfig(Config):
    a = 0
    b = "hello"


if __name__ == "__main__":
    print("Script is running")
    raise RuntimeError("An error occured!")
