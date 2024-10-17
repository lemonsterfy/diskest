"""
Database management module for Diskest
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ResultDatabase:
    """Manages the storage and retrieval of test results."""

    def __init__(self, db_path: str = "/var/lib/diskest/results.db"):
        self.db_path = Path(db_path)
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the database and create necessary tables."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            os.chmod(self.db_path.parent, 0o755)
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        data TEXT NOT NULL
                    )
                """
                )
            if self.db_path.exists():
                os.chmod(self.db_path, 0o644)
        except PermissionError:
            logger.error(f"No permission to create or modify database: {self.db_path}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database."""
        return sqlite3.connect(str(self.db_path))

    def save_result(self, result: Dict) -> Optional[int]:
        """
        Save a test result to the database.

        Args:
            result (Dict): Test result to save

        Returns:
            Optional[int]: ID of the saved result, or None if saving failed
        """
        with self._get_connection() as conn:
            try:
                cursor = conn.execute(
                    "INSERT INTO results (timestamp, data) VALUES (?, ?)",
                    (datetime.now().isoformat(), json.dumps(result)),
                )
                row_id = cursor.lastrowid
                logger.info(f"Result saved with ID: {row_id}")
                return row_id
            except sqlite3.Error as e:
                logger.error(f"Error saving results to database: {e}")
                return None

    def get_latest_result(self) -> Optional[Dict]:
        """
        Retrieve the latest test result from the database.

        Returns:
            Optional[Dict]: Latest test result, or None if no results found
        """
        with self._get_connection() as conn:
            try:
                cursor = conn.execute(
                    "SELECT id, data FROM results ORDER BY timestamp DESC LIMIT 1"
                )
                result = cursor.fetchone()
                if result:
                    logger.info(f"Retrieved result with ID: {result[0]}")
                    return json.loads(result[1])
                logger.warning("No results found in the database")
                return None
            except sqlite3.Error as e:
                logger.error(f"Error retrieving latest result from database: {e}")
                return None

    def get_all_results(self) -> List[Tuple[str, Dict]]:
        """
        Retrieve all test results from the database.

        Returns:
            List[Tuple[str, Dict]]: List of tuples
            containing timestamp and test result
        """
        with self._get_connection() as conn:
            try:
                cursor = conn.execute(
                    "SELECT timestamp, data FROM results ORDER BY timestamp DESC"
                )
                return [
                    (timestamp, json.loads(data))
                    for timestamp, data in cursor.fetchall()
                ]
            except sqlite3.Error as e:
                logger.error(f"Error retrieving all results from database: {e}")
                return []

    def delete_result(self, result_id: int) -> bool:
        """
        Delete a specific test result from the database.

        Args:
            result_id (int): ID of the result to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self._get_connection() as conn:
            try:
                conn.execute("DELETE FROM results WHERE id = ?", (result_id,))
                logger.info(f"Deleted result with ID: {result_id}")
                return True
            except sqlite3.Error as e:
                logger.error(f"Error deleting result from database: {e}")
                return False

    def clear_all_results(self) -> bool:
        """
        Clear all test results from the database.

        Returns:
            bool: True if clearing was successful, False otherwise
        """
        with self._get_connection() as conn:
            try:
                conn.execute("DELETE FROM results")
                logger.info("Cleared all results from database")
                return True
            except sqlite3.Error as e:
                logger.error(f"Error clearing all results from database: {e}")
                return False
