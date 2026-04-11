try:
    # Test core imports
    from app.core.config import settings
    print(f"✅ Config: {settings.PROJECT_NAME}")
    
    # Test models
    from models.anchor import Anchor
    print("✅ Anchor model imported")
    
    # Test schemas
    from schemas.anchor import AnchorCreate
    print("✅ AnchorCreate schema imported")
    
    # Create test schema instance
    test_data = {
        "user_id": "test_user",
        "content_type": "3d_object",
        "content_data": "{\"url\":\"test.glb\"}",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "altitude": 10.0
    }
    anchor_create = AnchorCreate(**test_data)
    print(f"✅ Schema validation: {anchor_create.content_type} at ({anchor_create.latitude}, {anchor_create.longitude})")
    
    # Test services
    from services.anchor import AnchorService
    print("✅ AnchorService imported")
    
    # Test database
    from app.db.session import get_db
    print("✅ Database session imported")
    
    # Test main app
    from app.main import app
    print("✅ FastAPI app imported")
    
    # Test endpoints
    from app.api.v1.endpoints.anchors import router
    print("✅ Anchors router imported")
    
    print("\n✅ All imports and validations successful!")
    print("Backend is ready for development.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
