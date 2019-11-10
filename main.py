from common import *

def main():
    # Setup db
    conn = db_connect(DATABASE_FILENAME)
    db_setup(conn)
    db_index(conn)

    db_make(conn)

    conn.close()


if __name__ == "__main__":
    main()
