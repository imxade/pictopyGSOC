import sqlite3
from typing import Generator, Tuple
from utils import *
from media import *

def populateMediaTable(conn: sqlite3.Connection, files: Generator[Tuple[str, str, str], None, None]) -> Generator[Tuple[int, str, str], None, None]:
    """
    Generate file hash.
    If hash already exists, update the path of existing media files.
    Otherwise, insert data of new media files.

    Args:
        conn: The database connection object.
        files: A generator of file paths.

    Yields:
        Tuples containing mediaID, file, and fileType.
    """
    for file, fileType, parentDir in files:
        fileHash = genHash(file)
        if updateMediaPath(conn, file, parentDir, fileHash):
            continue
        yield insertMedia(conn, fileHash, file, parentDir, fileType)

def classifyMedia(conn: sqlite3.Connection, objDetectionModel: str, rowsToClassify: Generator[Tuple[int, str, str], None, None]) -> None:
    """
    Classify media files.
    Establish relation between media files and classes,
    By inserting result into Junction Table.

    Args:
        conn: The database connection object.
        rowsToClassify: A generator of tuples containing mediaID, file, and fileType.
    """
    objDetectionModel = pathOf("models/yolov8n.onnx")
    for mediaID, file, fileType in rowsToClassify:
        try:
            if fileType == "vid":
                mediaClass = videoClasses(file, objDetectionModel)
            elif fileType == "img":
                mediaClass = imageClasses(file, objDetectionModel)
        except Exception as e:
            print(e)
            continue
        insertClassRelation(conn, mediaClass, mediaID)
