import localforage from 'localforage';

export interface SyncOperation {
  id: string; // idempotency key
  url: string;
  method: 'POST' | 'PUT' | 'PATCH';
  payload: any;
  timestamp: number;
}

const syncQueue = localforage.createInstance({
  name: 'coalmine-sync-queue',
});

export const addToSyncQueue = async (url: string, method: 'POST' | 'PUT' | 'PATCH', payload: any) => {
  const id = crypto.randomUUID();
  const operation: SyncOperation = {
    id,
    url,
    method,
    payload: { ...payload, idempotency_key: id },
    timestamp: Date.now(),
  };
  
  const currentQueue: SyncOperation[] = (await syncQueue.getItem('queue')) || [];
  currentQueue.push(operation);
  await syncQueue.setItem('queue', currentQueue);
  return id;
};

export const getSyncQueue = async (): Promise<SyncOperation[]> => {
  return (await syncQueue.getItem('queue')) || [];
};

export const clearSyncQueue = async () => {
  await syncQueue.setItem('queue', []);
};

export const flushSyncQueue = async () => {
  const queue = await getSyncQueue();
  if (queue.length === 0) return;

  const failedOps: SyncOperation[] = [];

  // Important endpoints: /api/v1/field/events and /api/v1/field/inspections
  for (const op of queue) {
    try {
      const response = await fetch(op.url, {
        method: op.method,
        headers: {
          'Content-Type': 'application/json',
          // Assuming auth header is managed via fetch wrapper usually, but this is simple fetch
          // You may need to augment this to include Authorization if not using cookies
        },
        body: JSON.stringify(op.payload),
      });

      if (!response.ok) {
        console.error('Sync failed for operation:', op.id, response.statusText);
        failedOps.push(op);
      }
    } catch (error) {
      console.error('Network error during sync:', op.id, error);
      failedOps.push(op);
    }
  }

  await syncQueue.setItem('queue', failedOps);
};
