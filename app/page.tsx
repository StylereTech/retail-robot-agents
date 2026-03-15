'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface DemoEvent {
  id: string;
  type: 'agent' | 'robot' | 'dispatch' | 'complete' | 'error';
  message: string;
  data: Record<string, unknown>;
  timestamp: string;
}

interface PickedItem {
  brand: string;
  name: string;
  ourPrice?: number;
  price?: number;
  imageUrl?: string;
  sku?: string;
  category?: string;
}

type RobotState = 'idle' | 'navigate' | 'pick' | 'return' | 'done';
type DemoState = 'idle' | 'running' | 'complete' | 'reconnecting' | 'error';
type TrackingStep = { label: string; done: boolean };

// ─── Iteration 4: WS URL — hardcoded fallback, NEVER localhost in production ──

const PROD_WS = 'wss://robot-api-production.up.railway.app';
const PROD_API = 'https://robot-api-production.up.railway.app';

function getWsUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_WS_URL;
  if (!envUrl || envUrl.includes('localhost') || envUrl.includes('127.0.0.1')) {
    // In production, hardcoded fallback — never localhost
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
      return `${PROD_WS}/ws/demo`;
    }
  }
  return envUrl ? `${envUrl}/ws/demo` : `${PROD_WS}/ws/demo`;
}

const WS_URL = getWsUrl();
const API_URL = process.env.NEXT_PUBLIC_API_URL || PROD_API;

const DEMO_CUSTOMER = {
  name: 'Alexandra Chen',
  sizes: { tops: 'S', bottoms: '26' },
  style_tags: ['minimalist', 'luxury', 'business'],
  budget_max: 2500,
  preferred_brands: ['Saint Laurent', 'Prada', 'Bottega Veneta'],
  occasion: 'business dinner',
};

const EVENT_COLORS: Record<string, string> = {
  agent: 'text-blue-400 border-blue-500',
  robot: 'text-orange-400 border-orange-500',
  dispatch: 'text-green-400 border-green-500',
  complete: 'text-emerald-300 border-emerald-400',
  error: 'text-red-400 border-red-500',
};

const EVENT_ICONS: Record<string, string> = {
  agent: '🤖', robot: '🦾', dispatch: '🚗', complete: '✅', error: '❌',
};

// ─── Iteration 7: Error Boundary ─────────────────────────────────────────────

import React from 'react';

interface ErrorBoundaryState { hasError: boolean; errorMsg: string }

class ErrorBoundary extends React.Component<
  { fallback: React.ReactNode; children: React.ReactNode },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, errorMsg: '' };

  static getDerivedStateFromError(e: Error): ErrorBoundaryState {
    return { hasError: true, errorMsg: e.message };
  }

  componentDidCatch(e: Error) {
    console.error('Panel error caught by boundary:', e);
  }

  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}

const PanelFallback = ({ label }: { label: string }) => (
  <div className="flex items-center justify-center h-full text-gray-600 text-xs">
    <div className="text-center">
      <div className="text-2xl mb-2">⚠️</div>
      <div>{label} temporarily unavailable</div>
      <div className="text-gray-700 mt-1">Reload to restore</div>
    </div>
  </div>
);

// ─── Robot Animation ──────────────────────────────────────────────────────────

function RobotArm({ state }: { state: RobotState }) {
  const armAngle = { idle: 0, navigate: -30, pick: 45, return: -20, done: 0 }[state];
  const isMoving = state === 'navigate' || state === 'pick' || state === 'return';

  return (
    <div className="flex flex-col items-center justify-center h-full relative">
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <div className="w-32 h-6 bg-gradient-to-r from-gray-700 via-gray-600 to-gray-700 rounded-full shadow-lg" />
      </div>
      <div
        className={`absolute bottom-14 left-1/2 -translate-x-1/2 transition-all duration-700 ${isMoving ? 'animate-pulse' : ''}`}
        style={{ transformOrigin: 'bottom center' }}
      >
        <div className="w-16 h-20 bg-gradient-to-b from-gray-500 to-gray-700 rounded-lg mx-auto relative border border-gray-500 shadow-xl">
          <div className="flex gap-2 justify-center pt-3">
            <div className={`w-3 h-3 rounded-full ${isMoving ? 'bg-orange-400 animate-ping' : 'bg-blue-400'}`} />
            <div className={`w-3 h-3 rounded-full ${isMoving ? 'bg-orange-400 animate-ping' : 'bg-blue-400'}`} />
          </div>
          <div className="mx-3 mt-2 h-6 bg-gray-800 rounded flex items-center justify-center">
            <div className={`w-2 h-2 rounded-full ${state === 'done' ? 'bg-green-400' : isMoving ? 'bg-orange-400' : 'bg-gray-500'}`} />
          </div>
        </div>
        <div
          className="absolute -right-8 top-2 w-14 h-4 bg-gradient-to-r from-gray-500 to-gray-400 rounded-full origin-left transition-transform duration-700 shadow-lg"
          style={{ transform: `rotate(${armAngle}deg)` }}
        >
          <div className="absolute right-0 -top-1 w-5 h-6 flex flex-col gap-1">
            <div className={`h-2 w-5 bg-orange-500 rounded transition-all duration-300 ${state === 'pick' ? 'translate-y-1' : ''}`} />
            <div className={`h-2 w-5 bg-orange-500 rounded transition-all duration-300 ${state === 'pick' ? '-translate-y-1' : ''}`} />
          </div>
        </div>
        <div className="absolute -left-8 top-2 w-14 h-4 bg-gradient-to-l from-gray-500 to-gray-400 rounded-full shadow-lg" />
      </div>
      <div className="absolute top-4 left-1/2 -translate-x-1/2 text-xs text-gray-400 uppercase tracking-widest">
        {{ idle: '● STANDBY', navigate: '▶ NAVIGATING', pick: '⊕ PICKING', return: '◀ RETURNING', done: '✓ COMPLETE' }[state]}
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function DemoPage() {
  const [events, setEvents] = useState<DemoEvent[]>([]);
  const [pickedItems, setPickedItems] = useState<PickedItem[]>([]);
  const [robotState, setRobotState] = useState<RobotState>('idle');
  const [demoState, setDemoState] = useState<DemoState>('idle');
  const [wsConnected, setWsConnected] = useState(false);
  const [trackingSteps, setTrackingSteps] = useState<TrackingStep[]>([]);
  const [orderTotal, setOrderTotal] = useState(0);
  const [dispatchStatus, setDispatchStatus] = useState('');
  const [reconnectCount, setReconnectCount] = useState(0);

  const feedRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const eventIdRef = useRef(0);
  const demoStateRef = useRef<DemoState>('idle');

  // Keep ref in sync
  useEffect(() => { demoStateRef.current = demoState; }, [demoState]);

  const addEvent = useCallback((evt: Omit<DemoEvent, 'id'>) => {
    const id = `evt-${++eventIdRef.current}`;
    setEvents(prev => [...prev, { ...evt, id }]);
  }, []);

  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [events]);

  // ── Iteration 16: WS keepalive ping ──────────────────────────────────────
  const startKeepalive = useCallback((ws: WebSocket) => {
    if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
    pingIntervalRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        try { ws.send(JSON.stringify({ type: 'ping' })); } catch { /* ignore */ }
      }
    }, 25000); // every 25s — under Railway's 60s idle timeout
  }, []);

  const stopKeepalive = useCallback(() => {
    if (pingIntervalRef.current) { clearInterval(pingIntervalRef.current); pingIntervalRef.current = null; }
  }, []);

  // ── Iteration 9: WS connect with reconnect logic ─────────────────────────
  const connectWS = useCallback((sendStartOnConnect = false, retryCount = 0) => {
    // Close existing connection cleanly
    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      wsRef.current.onclose = null; // prevent reconnect loop
      wsRef.current.close();
    }
    stopKeepalive();

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
      setReconnectCount(0);
      startKeepalive(ws);

      if (sendStartOnConnect) {
        // Send demo start message immediately on open
        ws.send(JSON.stringify({ customer: DEMO_CUSTOMER }));
      }
    };

    ws.onmessage = (msg) => {
      try {
        const raw = JSON.parse(msg.data as string);

        // Ignore pong / ping responses
        if (raw.type === 'pong' || raw.type === 'ping') return;

        const evt = raw as Omit<DemoEvent, 'id'>;
        addEvent(evt);

        // Robot state machine
        if (evt.type === 'robot') {
          const step = (evt.data?.step as string) || '';
          if (step === 'navigate') setRobotState('navigate');
          else if (step === 'pick') setRobotState('pick');
          else if (step === 'return') setRobotState('return');
          else if (step === 'done') setRobotState('done');

          // Collect picked items — backend sends data.picked (not data.item)
          const picked = evt.data?.picked as PickedItem | undefined;
          if (picked?.brand) {
            setPickedItems(prev => {
              const alreadyPicked = prev.some(p => p.sku === picked.sku);
              return alreadyPicked ? prev : [...prev, picked];
            });
          }
        }

        // Dispatch tracking
        if (evt.type === 'dispatch') {
          const steps = evt.data?.tracking_steps as TrackingStep[] | undefined;
          if (steps) setTrackingSteps(steps);
          const total = evt.data?.total as number | undefined;
          if (total) setOrderTotal(total);
          setDispatchStatus(evt.message);
        }

        // Complete
        if (evt.type === 'complete') {
          setRobotState('done');
          setDemoState('complete');
          stopKeepalive();
          const total = (evt.data?.total as number) || (evt.data?.summary as Record<string, number> | undefined)?.total_value || 0;
          if (total) setOrderTotal(total);
        }

        if (evt.type === 'error') {
          setDemoState('error');
          stopKeepalive();
        }
      } catch {
        // Malformed message — ignore, don't crash
      }
    };

    ws.onerror = () => {
      setWsConnected(false);
    };

    ws.onclose = () => {
      setWsConnected(false);
      stopKeepalive();

      // Auto-reconnect if demo was running (not a clean complete/idle)
      const currentState = demoStateRef.current;
      if (currentState === 'running' && retryCount < 3) {
        const delay = (retryCount + 1) * 2000;
        setDemoState('reconnecting');
        setReconnectCount(retryCount + 1);
        setTimeout(() => connectWS(false, retryCount + 1), delay);
      }
    };
  }, [addEvent, startKeepalive, stopKeepalive]);

  // Initial WS connection on mount
  useEffect(() => {
    connectWS(false, 0);
    return () => {
      stopKeepalive();
      if (wsRef.current) { wsRef.current.onclose = null; wsRef.current.close(); }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Demo start ────────────────────────────────────────────────────────────
  const handleRunDemo = useCallback(() => {
    if (demoState === 'running') return;

    // Reset state
    setEvents([]);
    setPickedItems([]);
    setRobotState('idle');
    setTrackingSteps([]);
    setOrderTotal(0);
    setDispatchStatus('');
    setDemoState('running');

    // Connect fresh WS and send start message on open
    connectWS(true, 0);
  }, [demoState, connectWS]);

  const isRunning = demoState === 'running';
  const isComplete = demoState === 'complete';
  const isReconnecting = demoState === 'reconnecting';

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* ── Top Bar ── */}
      <header className="h-16 border-b border-gray-800 flex items-center justify-between px-6 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="text-orange-500 font-bold text-xl tracking-tight">Style.re</div>
          <div className="text-gray-600">×</div>
          <div className="text-gray-300 font-medium text-sm">AI Robotics</div>
          <div className="ml-2 px-2 py-0.5 bg-orange-500/10 border border-orange-500/30 rounded text-orange-400 text-xs font-mono">
            LIVE DEMO
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* WS + reconnect status */}
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : isReconnecting ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'}`} />
            {isReconnecting ? `Reconnecting (${reconnectCount}/3)...` : wsConnected ? 'Connected' : 'Disconnected'}
          </div>

          {/* Run / Run Again button */}
          {isComplete ? (
            <button
              onClick={handleRunDemo}
              className="px-5 py-2 rounded-lg font-semibold text-sm bg-emerald-500 hover:bg-emerald-400 text-white shadow-lg shadow-emerald-500/20 transition-all"
            >
              ↺ Run Again
            </button>
          ) : (
            <button
              onClick={handleRunDemo}
              disabled={isRunning || isReconnecting}
              className={`px-5 py-2 rounded-lg font-semibold text-sm transition-all ${
                isRunning || isReconnecting
                  ? 'bg-orange-500/30 text-orange-300 cursor-not-allowed'
                  : 'bg-orange-500 hover:bg-orange-400 text-white shadow-lg shadow-orange-500/20 hover:shadow-orange-500/40'
              }`}
            >
              {isRunning ? '⟳ Running…' : isReconnecting ? '⟳ Reconnecting…' : '▶ Run Demo'}
            </button>
          )}
        </div>
      </header>

      {/* ── Three-panel layout ── */}
      <div className="flex flex-1 overflow-hidden">
        {/* ── LEFT: Agent Activity Feed ── */}
        <ErrorBoundary fallback={<PanelFallback label="Agent Feed" />}>
          <div className="w-72 border-r border-gray-800 flex flex-col flex-shrink-0">
            <div className="px-4 py-3 border-b border-gray-800">
              <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Agent Activity</div>
            </div>
            <div ref={feedRef} className="flex-1 overflow-y-auto p-3 space-y-2">
              {events.length === 0 ? (
                <div className="text-gray-600 text-xs text-center mt-8">
                  {demoState === 'idle' ? 'Press "Run Demo" to start' : 'Waiting for events...'}
                </div>
              ) : (
                events.filter(e => e.type !== 'complete').map((evt) => (
                  <div key={evt.id} className={`border-l-2 pl-3 py-1.5 ${EVENT_COLORS[evt.type] || 'text-gray-400 border-gray-600'}`}>
                    <div className="text-xs leading-snug">
                      <span className="mr-1">{EVENT_ICONS[evt.type] || '•'}</span>
                      {evt.message}
                    </div>
                    <div className="text-gray-600 text-xs mt-0.5 font-mono">
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </ErrorBoundary>

        {/* ── CENTER: Robot Visualization ── */}
        <ErrorBoundary fallback={<PanelFallback label="Robot Visualization" />}>
          <div className="flex-1 flex flex-col border-r border-gray-800 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-800">
              <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Robot Visualization</div>
            </div>
            <div className="flex-1 relative overflow-hidden">
              <div className="h-2/3 relative">
                <RobotArm state={robotState} />
                <div className="absolute bottom-0 left-0 right-0 h-12 opacity-10"
                  style={{ backgroundImage: 'repeating-linear-gradient(90deg, #FF6B00 0px, transparent 1px, transparent 40px)' }} />
              </div>
              <div className="h-1/3 border-t border-gray-800 px-4 py-3">
                <div className="text-xs text-gray-500 uppercase tracking-widest mb-2 font-semibold">
                  Dispatch Box {pickedItems.length > 0 && `(${pickedItems.length} items)`}
                </div>
                <div className="space-y-1.5 overflow-y-auto max-h-full">
                  {pickedItems.length === 0 ? (
                    <div className="text-gray-700 text-xs">No items picked yet</div>
                  ) : (
                    pickedItems.map((item, i) => (
                      <div key={`${item.sku || item.name}-${i}`} className="flex items-center gap-2 bg-gray-800 rounded-lg p-2 border border-orange-500/30">
                        <div className="w-10 h-10 rounded overflow-hidden bg-gray-700 flex-shrink-0">
                          {item.imageUrl ? (
                            <img
                              src={item.imageUrl}
                              alt={item.name || ''}
                              className="w-full h-full object-cover"
                              onError={(e) => { e.currentTarget.style.display = 'none'; }}
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-lg">👗</div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-orange-400 font-semibold truncate">{item.brand}</div>
                          <div className="text-xs text-gray-300 truncate">{item.name}</div>
                        </div>
                        <div className="text-xs text-white font-mono">
                          ${(item.ourPrice || item.price || 0).toLocaleString()}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </ErrorBoundary>

        {/* ── RIGHT: Order Summary ── */}
        <ErrorBoundary fallback={<PanelFallback label="Order Summary" />}>
          <div className="w-80 flex flex-col flex-shrink-0">
            <div className="px-4 py-3 border-b border-gray-800">
              <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Order Summary</div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Customer profile */}
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-full bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-lg">👤</div>
                  <div>
                    <div className="font-semibold text-sm">{DEMO_CUSTOMER.name}</div>
                    <div className="text-gray-500 text-xs">{DEMO_CUSTOMER.occasion}</div>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Budget</span>
                    <span className="text-white font-mono">${DEMO_CUSTOMER.budget_max.toLocaleString()}</span>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {DEMO_CUSTOMER.style_tags.map(tag => (
                      <span key={tag} className="px-2 py-0.5 bg-gray-800 text-gray-400 rounded text-xs border border-gray-700">{tag}</span>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {DEMO_CUSTOMER.preferred_brands.map(b => (
                      <span key={b} className="px-2 py-0.5 bg-orange-500/10 text-orange-400 rounded text-xs border border-orange-500/20">{b}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Curated items */}
              {pickedItems.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-widest mb-2 font-semibold">Curated Items</div>
                  <div className="space-y-2">
                    {pickedItems.map((item, i) => (
                      <div key={i} className="flex items-center gap-3 bg-gray-900 rounded-lg p-2.5 border border-gray-800">
                        <div className="w-12 h-12 rounded-lg overflow-hidden bg-gray-800 flex-shrink-0">
                          {item.imageUrl ? (
                            <img
                              src={item.imageUrl}
                              alt={item.name || ''}
                              className="w-full h-full object-cover"
                              onError={(e) => { e.currentTarget.style.display = 'none'; }}
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-xl">🛍️</div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-orange-400 font-semibold">{item.brand}</div>
                          <div className="text-xs text-gray-300 truncate">{item.name}</div>
                          <div className="text-sm font-mono text-white mt-0.5">
                            ${(item.ourPrice || item.price || 0).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-800">
                    <span className="text-gray-400 text-sm">Total</span>
                    <span className="text-white font-bold font-mono text-lg">
                      ${(orderTotal || pickedItems.reduce((s, i) => s + (i.ourPrice || i.price || 0), 0)).toLocaleString()}
                    </span>
                  </div>
                </div>
              )}

              {/* Dispatch tracking */}
              {trackingSteps.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-widest mb-3 font-semibold">Dispatch Status</div>
                  {dispatchStatus && (
                    <div className="text-xs text-green-400 mb-3 bg-green-500/10 border border-green-500/20 rounded-lg px-3 py-2">{dispatchStatus}</div>
                  )}
                  <div className="relative">
                    <div className="absolute left-3 top-3 bottom-3 w-px bg-gray-800" />
                    <div className="space-y-3">
                      {trackingSteps.map((step, i) => (
                        <div key={i} className="flex items-center gap-3 pl-1">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 z-10 text-xs ${step.done ? 'bg-green-500 text-white' : 'bg-gray-800 border border-gray-700 text-gray-600'}`}>
                            {step.done ? '✓' : i + 1}
                          </div>
                          <span className={`text-sm ${step.done ? 'text-white' : 'text-gray-600'}`}>{step.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Complete card */}
              {isComplete && (
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 text-center">
                  <div className="text-2xl mb-1">🎉</div>
                  <div className="text-emerald-300 font-semibold text-sm">Demo Complete!</div>
                  <div className="text-gray-400 text-xs mt-1">Style.re delivery on the way for {DEMO_CUSTOMER.name}</div>
                  <button
                    onClick={handleRunDemo}
                    className="mt-3 px-4 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-xs rounded-lg transition-all"
                  >
                    ↺ Run Again
                  </button>
                </div>
              )}
            </div>
          </div>
        </ErrorBoundary>
      </div>
    </div>
  );
}
