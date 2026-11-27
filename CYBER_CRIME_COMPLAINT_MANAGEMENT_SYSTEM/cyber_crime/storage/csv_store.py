import csv
from pathlib import Path


class CSVStore:
    """
    Simple CSV table. If the file on disk is missing columns
    (older version), it is upgraded automatically.
    """

    def __init__(self, path, fieldnames, key_field):
        self.path = Path(path)
        self.fieldnames = fieldnames
        self.key_field = key_field

        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.save_all([])
        else:
            self._migrate()

    def _migrate(self):
        with self.path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file, restval="")
            header = reader.fieldnames or []
            rows = list(reader)

        if header != self.fieldnames:
            self.save_all(rows)

    def get_all(self):
        with self.path.open("r", newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file, restval=""))

        for row in rows:
            for name in self.fieldnames:
                if row.get(name) is None:
                    row[name] = ""
        return rows

    def save_all(self, records):
        with self.path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.fieldnames,
                restval="",
                extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(records)

    def add(self, record):
        records = self.get_all()
        records.append(record)
        self.save_all(records)

    def find_by_key(self, value):
        for record in self.get_all():
            if record[self.key_field] == value:
                return record
        return None

    def update(self, value, updated_record):
        records = self.get_all()
        for index, record in enumerate(records):
            if record[self.key_field] == value:
                records[index] = updated_record
                self.save_all(records)
                return True
        return False

    def delete(self, value):
        records = [
            r for r in self.get_all()
            if r[self.key_field] != value
        ]
        self.save_all(records)
