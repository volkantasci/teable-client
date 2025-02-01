from teable import TeableClient, TeableConfig
from teable.models.view import View

def test_real_view_response():
    # API'den gelen örnek veri
    api_response = {
        'id': 'tblIXRravN7thPWwhfi',
        'name': 'Sadeleştirilmiş Türkçe - Kararlar',
        'filter': 'invalid',  # String olarak gelen filter verisi
        'sort': None
    }
    
    # View oluştur
    view = View.from_api_response(api_response)
    
    # Temel özellikleri kontrol et
    assert view.view_id == 'tblIXRravN7thPWwhfi'
    assert view.name == 'Sadeleştirilmiş Türkçe - Kararlar'
    assert len(view.filters) == 0  # Geçersiz filter verisi olduğu için boş liste olmalı
    assert len(view.sorts) == 0  # Sort verisi None olduğu için boş liste olmalı
