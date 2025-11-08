# 🔧 CRITICAL FIX: Reserved Word 'metadata' in SQLAlchemy

## The Issue

**Error:**
```
InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## Root Cause

In SQLAlchemy's Declarative API, **`metadata` is a reserved attribute name**. It's used internally by SQLAlchemy to store table metadata information. You CANNOT use `metadata` as a column name in your models.

From the error traceback:
```python
File "/home/adminuser/venv/lib/python3.13/site-packages/sqlalchemy/orm/decl_base.py", line 1529
    elif k in ("metadata",):
        raise exc.InvalidRequestError(
            f"Attribute name '{k}' is reserved when using the Declarative API."
        )
```

## The Fix

Renamed all `metadata` columns to avoid the conflict:

### Database Models (`app/models/database.py`)

**Before:**
```python
class Document(Base):
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class Chunk(Base):
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

**After:**
```python
class Document(Base):
    doc_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class Chunk(Base):
    chunk_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

### Updated References

**1. Document Service (`app/services/document_service.py`)**
```python
# Before
metadata=chunk.metadata
document.metadata = metadata

# After
chunk_metadata=chunk.metadata  # chunk.metadata from extraction
document.doc_metadata = metadata
```

**2. Retriever (`app/core/retrieval/retriever.py`)**
```python
# Before
"metadata": chunk.metadata or {}
if chunk.metadata and "page_number" in chunk.metadata:
    result["page"] = chunk.metadata["page_number"]

# After
"metadata": chunk.chunk_metadata or {}
if chunk.chunk_metadata and "page_number" in chunk.chunk_metadata:
    result["page"] = chunk.chunk_metadata["page_number"]
```

## Important Notes

### What IS `Base.metadata`?
In SQLAlchemy, `Base.metadata` is a special object that stores:
- Table definitions
- Column information
- Indexes
- Constraints
- Foreign keys

This is used by SQLAlchemy for:
```python
Base.metadata.create_all(bind=engine)  # Create tables
Base.metadata.drop_all(bind=engine)    # Drop tables
```

### SQLAlchemy Reserved Attributes

The following attribute names are RESERVED and CANNOT be used as column names:
- `metadata` - Table metadata
- `registry` - Mapper registry (in SQLAlchemy 2.0+)

## Verification

After this fix, the models should load without errors:
```bash
python -c "from app.models.database import Base, Document, Chunk; print('✅ Success!')"
```

## Files Changed

1. ✅ `app/models/database.py` - Renamed columns
2. ✅ `app/services/document_service.py` - Updated references
3. ✅ `app/core/retrieval/retriever.py` - Updated references

**Commit:** `aa5c765` - "Fix: Rename 'metadata' to 'doc_metadata' and 'chunk_metadata' (reserved word in SQLAlchemy)"

## Deployment Status

- **Fix pushed to GitHub**: ✅
- **Streamlit Cloud redeploying**: 🔄 In progress
- **ETA**: 3-5 minutes
- **Monitor**: Run `./monitor_deployment.sh`

---

**This should be the FINAL fix for the SQLAlchemy errors!** 🎉

The app will now:
1. ✅ Use DeclarativeBase (SQLAlchemy 2.0)
2. ✅ Use mapped_column() instead of Column()
3. ✅ Avoid reserved word 'metadata'
4. ✅ Store JSON data as text strings
5. ✅ Be fully Python 3.13 compatible
