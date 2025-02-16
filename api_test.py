import pytest
import requests
import uuid
from datetime import datetime, timezone

BASE_URL = "https://qa-internship.avito.com"
MAX_CREATION_TIME_SECONDS = 60
NON_EXISTENT_AD_ID = "11111111-1111-1111-1111-111111111111"

def validate_uuid(uuid_string):
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def validate_datetime(datetime_string):
    try:
        # Убираем последние 6 символов, т.к. UTC повторяется
        datetime.strptime(datetime_string[:-6], '%Y-%m-%d %H:%M:%S.%f %z')
        return True
    except ValueError:
        return False

def validate_statistic(data):
    assert isinstance(data['contacts'], int)
    assert isinstance(data['likes'], int)
    assert isinstance(data['viewCount'], int)

def validate_result(data):
    assert isinstance(data['result']['messages'], (dict, list))
    assert isinstance(data['result']['message'], str)

@pytest.fixture
def created_ad():
    payload = {
        "name": "Test Item",
        "price": 1000,
        "sellerId": 112211,
        "statistics": {
            "contacts": 10,
            "likes": 5,
            "viewCount": 20
        }
    }
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)

    # id объявления указан в поле status в последних 36 символах
    return response.json()['status'][-36:]

# 1. Создание объевления
class TestCreateAd:
    valid_payload = {
        "name": "Корректное объявление",
        "price": 1000,
        "sellerId": 112211,
        "statistics": {
            "contacts":3,
            "likes":123,
            "viewCount":12
        }
    }

# Положительные тесты 1.1-1.3
    @pytest.mark.xfail(reason="BUG: в созданном объявление name всегда равен \"dsdsd\" вместо указанного при создании")
    @pytest.mark.parametrize("seller_id", [112211, 999999, 111111])
    def test_create_ad_valid(self, seller_id):
        payload = self.valid_payload.copy()
        payload["sellerId"] = seller_id
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        post_request_time = datetime.now(timezone.utc)
        
        assert response.status_code == 200
        data = response.json()
        ad_id = data['status'][-36:]
        assert validate_uuid(ad_id)
        
        # Проверка созданного объявления
        get_response = requests.get(f"{BASE_URL}/api/1/item/{ad_id}")
        assert get_response.status_code == 200
        ad_data = get_response.json()[0]
        assert ad_data['name'] == payload['name']
        assert ad_data['price'] == payload['price']
        assert ad_data['sellerId'] == payload['sellerId']
        assert validate_datetime(ad_data['createdAt'])
        ad_creation_time = datetime.strptime(ad_data['createdAt'][:-6], '%Y-%m-%d %H:%M:%S.%f %z')
        assert (ad_creation_time - post_request_time).total_seconds <= MAX_CREATION_TIME_SECONDS

# Негативные тесты 1.4-1.20
    @pytest.mark.xfail(reason="BUG: объявление успешно создается, несмотря на отсутствие полей")
    @pytest.mark.parametrize("missing_field", ["sellerId", "name", "price", "statistics"])
    def test_missing_required_fields(self, missing_field):
        payload = self.valid_payload.copy()
        del payload[missing_field]
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == 400

    @pytest.mark.parametrize("invalid_seller_id", ["3452A", 345.2, True])
    def test_invalid_seller_id_type(self, invalid_seller_id):
        payload = self.valid_payload.copy()
        payload["sellerId"] = invalid_seller_id
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == 400

    @pytest.mark.parametrize("invalid_price", ["100", 100.5, True])
    def test_invalid_price_type(self, invalid_price):
        payload = self.valid_payload.copy()
        payload["price"] = invalid_price
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == 400

    @pytest.mark.parametrize("invalid_name", [1234, 123.45, True])
    def test_invalid_name_type(self, invalid_name):
        payload = self.valid_payload.copy()
        payload["name"] = invalid_name
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == 400

    @pytest.mark.xfail(reason="BUG: объявление успешно создается, несмотря на пустое название")
    def test_empty_name(self):
        payload = self.valid_payload.copy()
        payload["name"] = ""
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == 400

    @pytest.mark.xfail(reason="BUG: объявление успешно создается, несмотря на не входящие в диапазон (111111-999999) значения идентификатора продавца")
    @pytest.mark.parametrize("seller_id", [111110, 1000000])
    def test_seller_id_boundaries(self, seller_id):
        payload = self.valid_payload.copy()
        payload["sellerId"] = seller_id
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == 400

    @pytest.mark.xfail(reason="BUG: объявление успешно создается с отрицательной ценой")
    def test_negative_price(self):
        payload = self.valid_payload.copy()
        payload["price"] = -100
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == 400

# 2. Получение объявлений по ID
class TestGetAd:
# Положительные тесты 2.1
    def test_get_existing_ad(self, created_ad):
        response = requests.get(f"{BASE_URL}/api/1/item/{created_ad}")
        assert response.status_code == 200
        data = response.json()[0]
        
        assert validate_uuid(data['id'])
        assert isinstance(data['name'], str)
        assert isinstance(data['price'], int)
        assert 111111 <= data['sellerId'] <= 999999
        assert validate_datetime(data['createdAt'])
        assert isinstance(data['statistics']['contacts'], int)
        assert isinstance(data['statistics']['likes'], int)
        assert isinstance(data['statistics']['viewCount'], int)

# Негативные тесты 2.2-2.3
    @pytest.mark.xfail(reason="BUG?: 'messages' имеет тип NoneType, а должен быть dict")
    def test_get_non_existent_ad(self):
        response = requests.get(f"{BASE_URL}/api/1/item/{NON_EXISTENT_AD_ID}")
        assert response.status_code == 404
        data = response.json()
        validate_result(data)
        assert data['status'] == '404'

    def test_invalid_id_format(self):
        response = requests.get(f"{BASE_URL}/api/1/item/1234")
        assert response.status_code == 400
        data = response.json()
        validate_result(data)
        assert data['status'] == '400'

# 3. Получение всех объявлений по ID продавца 
class TestGetBySeller:
    @pytest.fixture
    def seller_with_ads(self):
        seller_id = 112212

        for _ in range(2):
            payload = {
                "name": "Test Item",
                "price": 1000,
                "sellerId": seller_id,
                "statistics": {
                    "contacts": 10,
                    "likes": 5,
                    "viewCount": 20
                }
            }
            requests.post(f"{BASE_URL}/api/1/item", json=payload)
        return seller_id
    
# Положительные тесты 3.1-3.2
    def test_get_ads_valid_seller(self, seller_with_ads):
        response = requests.get(f"{BASE_URL}/api/1/{seller_with_ads}/item")
        assert response.status_code == 200
        data = response.json()
        for ad in data:
            assert ad['sellerId'] == seller_with_ads

    def test_get_ads_empty_response(self):
        new_seller_id = 112233
        response = requests.get(f"{BASE_URL}/api/1/{new_seller_id}/item")
        assert response.status_code == 200
        assert len(response.json()) == 0

# Негативные тесты 3.3-3.5
    @pytest.mark.xfail(reason="BUG: при не входящих в диапазон (111111-999999) значениях идентификаторах продавца статус ответа - 200")
    @pytest.mark.parametrize("seller_id", [111110, 1000000])
    def test_out_of_range_seller_ids(self, seller_id):
        response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
        assert response.status_code == 400

    @pytest.mark.parametrize("seller_id", ["invalid_type", True, 123.45])
    def test_invalid_seller_ids_format(self, seller_id):
        response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
        assert response.status_code == 400

#  4. Получение статистики по ID объявления 
class TestStatistics:
# Положительные тесты 4.1
    def test_statistics_valid_id(self, created_ad):
        response = requests.get(f"{BASE_URL}/api/1/statistic/{created_ad}")
        assert response.status_code == 200
        data = response.json()[0]
        validate_statistic(data)

# Негативные тесты 4.2-4.3
    def test_statistics_non_existent(self):
        response = requests.get(f"{BASE_URL}/api/1/statistic/{NON_EXISTENT_AD_ID}")
        assert response.status_code == 404

    def test_statistics_invalid_id(self):
        response = requests.get(f"{BASE_URL}/api/1/statistic/1234")
        assert response.status_code == 400