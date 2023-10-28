import chromadb
from distutils.dir_util import copy_tree # used to create a backup

# TODO: Automatically backup Client
class MemoryDB:
    def __init__(self, path):
        self.dbPath = path
        self.chromaClient = chromadb.PersistentClient(path)

        self.chromaCollection = self.chromaClient.get_or_create_collection(name="MemoryDB")

    def newDBEntry(self, type: str, identifier: str, content: str):
        if self.entryExists(type, identifier):
            print(f"MemoryDB: Entry of type '{type}' with identifier '{identifier}' already exists in database.\n")
            return -1

        self.chromaCollection.add(ids=[str(self.chromaCollection.count()+1)],
                                  metadatas=[{"type" : type, "identifier" : identifier}],
                                  documents=content)

        print(f"MemoryDB: New entry with id '{self.chromaCollection.count()}' has been created.\n")

        return 0

    def updateDBEntry(self, type: str, identifier: str, content: str):
        if self.entryExists(type, identifier) is False:
            print(f"MemoryDB: Could not update entry with type '{type}' and identifier '{identifier}' as none was found")
            return

        # if content == "": # implement functionality to delete the entry and then adjusts the ids accordingly
        #     print("The new content you specified contains no characters.\nWould you like to delete the record? y/n")
        #     if input() == 'y':
        #         pass

        self.chromaCollection.update(ids=self.getId(type=type, identifier=identifier), documents=content)

    def entryExists(self, type: str, identifier: str) -> bool:
        if self.chromaCollection.get(where={
                                                "$and" : [
                                                        {"type" : {"$eq" : type}},
                                                        {"identifier" : {"$eq" : identifier}}
                                                    ]
                                                }
                                         )['documents']:
            return True

        print(f"MemoryDB: No entry of type '{type}' with identifier '{identifier}' was found in the database.\n")
        return False

    def updateOrCreateDBEntry(self, type: str, identifier: str, content: str):
        if self.entryExists(type=type, identifier=identifier):
            self.updateDBEntry(type=type, identifier=identifier, content=content)
        else:
            self.newDBEntry(type=type, identifier=identifier, content=content)

    def getId(self, type: str, identifier: str, content: str = None):
        result = self.chromaCollection.get(where={
                                                "$and" : [
                                                        {"type" : {"$eq" : type}},
                                                        {"identifier" : {"$eq" : identifier}}
                                                    ]
                                                }
                                         )
        return result["ids"][0]

    def vectorQueryDB(self, query: str) -> str:
        response = self.chromaCollection.query(query_texts=[query], n_results=1)['documents']
        if not response:
            print(f"MemoryDB: No entry found.\n")
            return ""
        return response[0][0]
    def metadataQueryDB(self, id: str = None, type: str = None, identifier: str = None):
        if id is not None:
            temp = self.chromaCollection.get(ids=[id])['documents']
            if not temp:
                print(f"MemoryDB: No entry with id '{id}' found.\n")
                return ""
            return temp[0]

        temp = self.chromaCollection.get(where={
                                                "$and" : [
                                                        {"type" : {"$eq" : type}},
                                                        {"identifier" : {"$eq" : identifier}}
                                                    ]
                                                }
                                         )['documents']

        if not temp:
            print(f"MemoryDB: No entry with type '{type}' and identifier '{identifier}' found.\n")
            return ""
        return temp[0]

    def backupDB(self, backupPath):
        try:
            copy_tree(self.dbPath, backupPath)
            print(f"MemoryDB: Successfully created a backup at location '{backupPath}'.")
        except Exception:
            print(f"MemoryDB: Failed to create a backup at location '{backupPath}', DB not affected.")
