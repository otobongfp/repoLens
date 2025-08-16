// IndexedDB storage utility for caching repository analysis results

interface CacheEntry {
  id: string;
  data: any;
  timestamp: number;
  folderPath: string;
}

class RepositoryCache {
  private dbName = "repolens-cache";
  private dbVersion = 1;
  private storeName = "repository-analysis";
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object store if it doesn't exist
        if (!db.objectStoreNames.contains(this.storeName)) {
          const store = db.createObjectStore(this.storeName, { keyPath: "id" });
          store.createIndex("folderPath", "folderPath", { unique: false });
          store.createIndex("timestamp", "timestamp", { unique: false });
        }
      };
    });
  }

  private async ensureDB(): Promise<void> {
    if (!this.db) {
      await this.init();
    }
  }

  async set(folderPath: string, data: any): Promise<void> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readwrite");
      const store = transaction.objectStore(this.storeName);

      const entry: CacheEntry = {
        id: this.generateId(folderPath),
        data,
        timestamp: Date.now(),
        folderPath,
      };

      const request = store.put(entry);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async get(folderPath: string): Promise<any | null> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readonly");
      const store = transaction.objectStore(this.storeName);
      const index = store.index("folderPath");

      const request = index.get(folderPath);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const result = request.result;
        if (result) {
          // Check if cache is still valid (24 hours)
          const isExpired = Date.now() - result.timestamp > 24 * 60 * 60 * 1000;
          if (isExpired) {
            this.delete(folderPath);
            resolve(null);
          } else {
            resolve(result.data);
          }
        } else {
          resolve(null);
        }
      };
    });
  }

  async delete(folderPath: string): Promise<void> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readwrite");
      const store = transaction.objectStore(this.storeName);
      const index = store.index("folderPath");

      // First get the entry to find its ID
      const getRequest = index.get(folderPath);

      getRequest.onerror = () => reject(getRequest.error);
      getRequest.onsuccess = () => {
        const entry = getRequest.result;
        if (entry) {
          // Delete using the entry's ID
          const deleteRequest = store.delete(entry.id);
          deleteRequest.onerror = () => reject(deleteRequest.error);
          deleteRequest.onsuccess = () => resolve();
        } else {
          resolve(); // Nothing to delete
        }
      };
    });
  }

  async clear(): Promise<void> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readwrite");
      const store = transaction.objectStore(this.storeName);

      const request = store.clear();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async getStats(): Promise<{ count: number; size: number }> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readonly");
      const store = transaction.objectStore(this.storeName);

      const countRequest = store.count();
      const getAllRequest = store.getAll();

      let count = 0;
      let size = 0;

      countRequest.onsuccess = () => {
        count = countRequest.result;
      };

      getAllRequest.onsuccess = () => {
        const entries = getAllRequest.result;
        size = new Blob([JSON.stringify(entries)]).size;
        resolve({ count, size });
      };

      countRequest.onerror = () => reject(countRequest.error);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    });
  }

  async getMostRecent(): Promise<CacheEntry | null> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readonly");
      const store = transaction.objectStore(this.storeName);
      const index = store.index("timestamp");

      const request = index.openCursor(null, "prev");

      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          resolve(cursor.value);
        } else {
          resolve(null);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  private generateId(folderPath: string): string {
    // Create a hash of the folder path for consistent IDs
    let hash = 0;
    for (let i = 0; i < folderPath.length; i++) {
      const char = folderPath.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return `repo_${Math.abs(hash)}`;
  }
}

// Export singleton instance
export const repositoryCache = new RepositoryCache();
