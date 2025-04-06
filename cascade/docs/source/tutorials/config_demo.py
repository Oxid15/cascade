from cascade.base import Config


class TrainConfig(Config):
    lr = 1e-6
    batch_size = 16
    total_iterations = 10000
    image_size = (200, 200)


def use_as_object(cfg: TrainConfig):
    print(f"This config is for {cfg.total_iterations} iterations")


def use_as_kwargs(lr, batch_size, total_iterations, image_size):
    print(f"Image height is {image_size[0]} and width is {image_size[1]}")


if __name__ == "__main__":
    cfg = TrainConfig()

    use_as_object(cfg)

    use_as_kwargs(**cfg.to_dict())
