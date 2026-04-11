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
    
    # Test services
    from services.anchor import AnchorService
    print("✅ AnchorService imported")
    
    # Test database
    from app.db.session import get_db
    print("✅ Database session imported")
    
    # Test main app
    from app.main import app
    print("✅ FastAPI app imported")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
