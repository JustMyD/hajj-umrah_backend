from dataclasses import dataclass
from decimal import Decimal

# Currencies = Literal["$", "₽"]
# class Currencies(Enum):
#    dollar = "$"
#    rubles = "₽"


@dataclass(frozen=True)
class Price:
    amount: Decimal  # use Decimal to avoid float issues
    currency: str  # Значение из таблицы currencies

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Price.amount must be >= 0")