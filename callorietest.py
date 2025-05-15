from calloriebot import get_product_data

def test_apple():
    result = get_product_data("яблоко", 200)
    assert result == {
        "calories": 104.0,
        "proteins": 0.6,
        "fats": 0.4,
        "carbs": 28.0
    }

def test_unknown():
    assert get_product_data("неизвестный", 100) is None

def test_cheese_100g():
    result = get_product_data("сыр", 100)
    assert result["calories"] == 350.0
    assert result["proteins"] == 25.0
    assert result["fats"] == 28.0
    assert result["carbs"] == 0.0

def test_milk_200g():
    result = get_product_data("молоко", 200)
    assert result["calories"] == 84.0
    assert result["proteins"] == 6.8
    assert result["fats"] == 2.0
    assert result["carbs"] == 10.0

def test_invalid_mass():
    result = get_product_data("молоко", -100)
    assert result is None

def test_unknown_product():
    result = get_product_data("кечуп", 50)
    assert result is None
