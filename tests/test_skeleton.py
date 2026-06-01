"""
Starter tests for Mutation Shootout.
"""
import pytest
from billing import (
    price_with_tax, apply_coupon, compute_total, booking_fee,
    compute_subtotal, convert_currency
)

class TestPriceWithTax:
    def test_positive_value(self):
        assert price_with_tax(100, 0.2) == 120
        assert price_with_tax(50, 0.1) == 55

    def test_zero_returns_zero(self):
        assert price_with_tax(0, 0.2) == 0

    @pytest.mark.parametrize("negative", [-1.0, -100])
    def test_negative_raises(self, negative):
        with pytest.raises(ValueError):
            price_with_tax(negative, 0.2)

    def test_high_tax_rate(self):
        assert price_with_tax(100, 1.0) == 200  # 100 % налог

    def test_no_tax(self):
        assert price_with_tax(100, 0) == 100

    def test_tax_calculation_edge(self):
        # Проверяем, что налог добавляется, а не вычитается
        assert price_with_tax(100, 0.1) > 100

    def test_exact_tax_amount(self):
        assert price_with_tax(100, 0.2) == 120  # Точное значение



class TestApplyCoupon:
    def test_valid_coupon(self):
        # Тестируем разные типы купонов
        assert apply_coupon(100, "SAVE10") == 90  # 10 % скидка
        assert apply_coupon(200, "FIXED50") == 150  # Фиксированная скидка 50

    def test_invalid_coupon(self):
        with pytest.raises(ValueError):
            apply_coupon(100, "UNKNOWN")

    def test_coupon_zero_amount(self):
        assert apply_coupon(0, "SAVE10") == 0

    def test_large_discount(self):
        # Купон даёт скидку больше суммы
        assert apply_coupon(50, "OVER50") == 0  # Сумма не может быть отрицательной

    def test_negative_input_validation(self):
        with pytest.raises(ValueError, match="Price must be positive"):
            apply_coupon(-10, "SAVE20")



class TestPipeline:
    def test_happy_flow_eur(self):
        items = [{"price": 100, "quantity": 2}]
        result = compute_total(items, currency="EUR", tax_rate=0.2, fee=10)
        assert result == 250  # (100×2)×1.2 + 10

    def test_happy_flow_with_coupon(self):
        items = [{"price": 200, "quantity": 1}]
        result = compute_total(
            items,
            currency="USD",
            tax_rate=0.1,
            fee=5,
            coupon="SAVE20"
        )
        assert result == 185  # (200−40)×1.1 + 5

    def test_empty_items(self):
        result = compute_total([], currency="EUR")
        assert result == 0

    def test_multiple_items(self):
        items = [
            {"price": 50, "quantity": 3},
            {"price": 10, "quantity": 5}
        ]
        result = compute_total(items, tax_rate=0.15, fee=0)
        expected = (50 * 3 + 10 * 5) * 1.15
        assert result == expected

    def test_currency_conversion(self):
        items = [{"price": 100, "quantity": 1}]
        result = compute_total(items, currency="USD", tax_rate=0, fee=0)
        # Предполагаем курс конвертации 1:1 для простоты
        assert result == 100

    def test_booking_fee_included(self):
        items = [{"price": 50, "quantity": 2}]
        result = compute_total(items, fee=booking_fee(100))
        assert result > 100  # С учётом комиссии
