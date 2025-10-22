"""Tests for FileStore - Safe Writes and Content Hashing"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.core.filestore import FileStore, compute_sha256, get_filestore


class TestComputeSHA256:
    """Test SHA256 hash computation"""
    
    def test_hash_string(self):
        """String input produces consistent hash"""
        content = "Hello, World!"
        hash1 = compute_sha256(content)
        hash2 = compute_sha256(content)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 is 64 hex chars
    
    def test_hash_bytes(self):
        """Bytes input produces consistent hash"""
        content = b"Hello, World!"
        hash1 = compute_sha256(content)
        hash2 = compute_sha256(content)
        
        assert hash1 == hash2
    
    def test_hash_different_content(self):
        """Different content produces different hashes"""
        hash1 = compute_sha256("content1")
        hash2 = compute_sha256("content2")
        
        assert hash1 != hash2
    
    def test_hash_known_value(self):
        """Verify against known SHA256 value"""
        # "test" -> 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
        result = compute_sha256("test")
        expected = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        assert result == expected


class TestFileStore:
    """Test FileStore safe write operations"""
    
    @pytest.fixture
    def temp_store(self):
        """Create temporary file store for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        store = FileStore(temp_dir)
        yield store
        shutil.rmtree(temp_dir)
    
    def test_safe_write_creates_file(self, temp_store):
        """safe_write creates file with correct content"""
        content = "Test content"
        result = temp_store.safe_write("test.txt", content)

        assert result["path"].exists()
        assert result["path"].read_text() == content
        assert result["size_bytes"] == len(content)
        assert result["sha256"] == compute_sha256(content)
        assert result["wrote"] is True
        assert result["reason"] == "created"
    
    def test_safe_write_creates_parent_dirs(self, temp_store):
        """safe_write creates parent directories automatically"""
        content = "Nested file"
        result = temp_store.safe_write("a/b/c/test.txt", content)
        
        assert result["path"].exists()
        assert result["path"].parent.parent.parent.name == "a"
    
    def test_safe_write_overwrite_mode(self, temp_store):
        """Overwrite mode replaces existing file"""
        temp_store.safe_write("test.txt", "original")
        result = temp_store.safe_write("test.txt", "updated", mode="overwrite")
        
        assert result["path"].read_text() == "updated"
        assert result["sha256"] == compute_sha256("updated")
        assert result["wrote"] is True
        assert result["reason"] == "overwritten"
    
    def test_safe_write_create_new_fails_if_exists(self, temp_store):
        """create_new mode fails if file already exists with different content"""
        temp_store.safe_write("test.txt", "original")
        
        with pytest.raises(FileExistsError):
            temp_store.safe_write("test.txt", "different", mode="create_new")
    
    def test_safe_write_create_new_idempotent(self, temp_store):
        """create_new mode is idempotent for same content"""
        content = "same content"
        result1 = temp_store.safe_write("test.txt", content, mode="create_new")
        result2 = temp_store.safe_write("test.txt", content, mode="create_new")
        
        assert result1["sha256"] == result2["sha256"]
        assert result1["size_bytes"] == result2["size_bytes"]
        assert result2["wrote"] is False
        assert result2["reason"] == "nochange"
    
    def test_safe_write_append_mode(self, temp_store):
        """Append mode adds to existing file"""
        temp_store.safe_write("test.txt", "Line 1\n")
        result = temp_store.safe_write("test.txt", "Line 2\n", mode="append")
        
        assert result["path"].read_text() == "Line 1\nLine 2\n"
        assert result["wrote"] is True
        assert result["reason"] == "appended"
    
    def test_duplicate_detection_skips_rewrite(self, temp_store):
        """Duplicate content detection skips unnecessary writes"""
        content = "Same content"
        
        result1 = temp_store.safe_write("test.txt", content)
        mtime1 = result1["path"].stat().st_mtime
        
        # Write again with same content
        result2 = temp_store.safe_write("test.txt", content)
        mtime2 = result2["path"].stat().st_mtime
        
        # Hash should match, file not rewritten
        assert result1["sha256"] == result2["sha256"]
        assert mtime1 == mtime2  # File not modified
        assert result2["wrote"] is False
        assert result2["reason"] == "nochange"
    
    def test_read_file(self, temp_store):
        """read() retrieves file content"""
        content = b"Binary content"
        temp_store.safe_write("test.bin", content)
        
        read_content = temp_store.read("test.bin")
        assert read_content == content
    
    def test_exists_check(self, temp_store):
        """exists() correctly identifies file presence"""
        assert not temp_store.exists("nonexistent.txt")
        
        temp_store.safe_write("exists.txt", "content")
        assert temp_store.exists("exists.txt")
    
    def test_list_files(self, temp_store):
        """list_files returns all files matching pattern"""
        temp_store.safe_write("a.txt", "content")
        temp_store.safe_write("b.py", "code")
        temp_store.safe_write("sub/c.txt", "nested")

        all_files = temp_store.list_files()
        assert len(all_files) == 3

        txt_files = temp_store.list_files("**/*.txt")
        assert len(txt_files) == 2

    def test_idempotency_preserves_hash(self, temp_store):
        """Idempotent writes preserve content hash"""
        content = "Idempotent content test"

        # First write
        result1 = temp_store.safe_write("test.txt", content)
        hash1 = result1["sha256"]

        # Second write with same content
        result2 = temp_store.safe_write("test.txt", content)
        hash2 = result2["sha256"]

        # Hashes should match
        assert hash1 == hash2
        assert result2["wrote"] is False
        assert result2["reason"] == "nochange"

    def test_nochange_reason(self, temp_store):
        """safe_write returns 'nochange' reason when content is identical"""
        content = "Unchanged content"

        # Initial write
        result1 = temp_store.safe_write("test.txt", content, mode="overwrite")
        assert result1["wrote"] is True
        assert result1["reason"] == "created"

        # Write same content again
        result2 = temp_store.safe_write("test.txt", content, mode="overwrite")
        assert result2["wrote"] is False
        assert result2["reason"] == "nochange"
        assert result2["sha256"] == result1["sha256"]


class TestFileStoreThreadSafety:
    """Test FileStore behavior under concurrent access"""
    
    @pytest.fixture
    def temp_store(self):
        temp_dir = Path(tempfile.mkdtemp())
        store = FileStore(temp_dir)
        yield store
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_concurrent_writes_same_file(self, temp_store):
        """Concurrent writes to same file are safe (one wins)"""
        import asyncio
        
        async def write_task(content):
            return await asyncio.to_thread(
                temp_store.safe_write,
                "shared.txt",
                content,
                mode="overwrite"
            )
        
        # Write different content concurrently
        results = await asyncio.gather(
            write_task("Content A"),
            write_task("Content B"),
            write_task("Content C")
        )
        
        # One of them should succeed, file should exist
        final_content = temp_store.read("shared.txt").decode()
        assert final_content in ["Content A", "Content B", "Content C"]
    
    @pytest.mark.asyncio
    async def test_concurrent_writes_different_files(self, temp_store):
        """Concurrent writes to different files all succeed"""
        import asyncio
        
        async def write_file(i):
            return await asyncio.to_thread(
                temp_store.safe_write,
                f"file_{i}.txt",
                f"Content {i}"
            )
        
        results = await asyncio.gather(*[write_file(i) for i in range(10)])
        
        # All files should exist
        files = temp_store.list_files()
        assert len(files) == 10


def test_get_filestore_singleton():
    """get_filestore returns same instance for same base_dir"""
    store1 = get_filestore(Path("."))
    store2 = get_filestore(Path("."))
    
    assert store1 is store2  # Same instance

