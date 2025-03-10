from cascade.base import Config
from cascade.lines import ModelLine
from cascade.models import BasicModel


class TrainConfig(Config):
    lr = 1e-6
    batch_size = 16
    total_iterations = 10000
    image_size = (200, 200)


if __name__ == "__main__":
    cfg = TrainConfig()

    line = ModelLine("line", model_cls=BasicModel)
    model = line.create_model()

    model.add_config()

    line.save(model)
