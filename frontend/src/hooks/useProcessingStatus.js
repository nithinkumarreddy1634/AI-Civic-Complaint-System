import { useState, useEffect, useCallback, useRef } from 'react';
import complaintService from '../services/complaintService';

export const useProcessingStatus = (complaintId, initialStatus = null, onComplete = null) => {
  const [statusData, setStatusData] = useState({
    processing_state: initialStatus?.processing_state || 'PENDING',
    progress: initialStatus?.processing_progress || 0,
    message: initialStatus?.processing_message || 'Initializing AI pipeline...',
    error: null,
  });
  const [isPolling, setIsPolling] = useState(false);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  const fetchStatus = useCallback(async () => {
    if (!complaintId) return null;
    try {
      const data = await complaintService.getProcessingStatus(complaintId);
      setStatusData({
        processing_state: data.processing_state,
        progress: data.progress,
        message: data.message,
        error: data.error,
      });

      if (data.processing_state === 'COMPLETE' || data.processing_state === 'FAILED') {
        setIsPolling(false);
        if (data.processing_state === 'COMPLETE' && onCompleteRef.current) {
          onCompleteRef.current(data);
        }
      }
      return data;
    } catch (err) {
      console.error('Error fetching processing status:', err);
      return null;
    }
  }, [complaintId]);

  useEffect(() => {
    if (!complaintId) return;

    // Check if initial status indicates already finished
    const state = statusData.processing_state;
    if (state === 'COMPLETE' || state === 'FAILED') {
      setIsPolling(false);
      return;
    }

    setIsPolling(true);
    let intervalId = null;

    const runPoll = async () => {
      const result = await fetchStatus();
      if (!result || result.processing_state === 'COMPLETE' || result.processing_state === 'FAILED') {
        if (intervalId) clearInterval(intervalId);
      }
    };

    // First fetch immediately
    runPoll();

    // Then poll every 2000ms
    intervalId = setInterval(runPoll, 2000);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [complaintId, fetchStatus]);

  return {
    ...statusData,
    isProcessing: isPolling && statusData.processing_state !== 'COMPLETE' && statusData.processing_state !== 'FAILED',
    isComplete: statusData.processing_state === 'COMPLETE',
    isFailed: statusData.processing_state === 'FAILED',
    refetch: fetchStatus,
  };
};

export default useProcessingStatus;
