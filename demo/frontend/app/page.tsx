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
  price: number;
  imageUrl?: string;
  sku?: string;
}

type RobotState = 'idle' | 'navigate' | 'pick' | 'return' | 'done';

type TrackingStep = { label: string; done: boolean };

// ─── Constants ────────────────────────────────────────────────────────────────

const WS_URL = process.env.NEXT_PUBLIC_WS_URL
  ? `${process.env.NEXT_PUBLIC_WS_URL}/ws/demo`
  : 'ws://localhost:8000/ws/demo';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const DEMO_CUSTOMER = {
  name: 'Alexandra Chen',
  sizes: { tops: 'S', bottoms: '26' },
  style_tags: ['minimalist', 'luxury', 'business'],
  budget_max: 2500,
  preferred_brands: ['Saint Laurent', 'Prada', 'Bottega Veneta'],
  occasion: 'business dinner',
};

const EVENT_COLORS: Record<DemoEvent['type'], string> = {
  agent: 'text-blue-400 border-blue-500',
  robot: 'text-orange-400 border-orange-500',
  dispatch: 'text-green-400 border-green-500',
  complete: 'text-emerald-300 border-emerald-400',
  error: 'text-red-400 border-red-500',
};

const EVENT_ICONS: Record<DemoEvent['type'], string> = {
  agent: '🤖',
  robot: '🦾',
  dispatch: '🚗',
  complete: '✅',
  error: '❌',
};

// ─── Robot Animation ──────────────────────────────────────────────────────────

function RobotArm({ state }: { state: RobotState }) {
  const armAngle = {
    idle: 0,
    navigate: -30,
    pick: 45,
    return: -20,
    done: 0,
  }[state];

  const isMoving = state === 'navigate' || state === 'pick' || state === 'return';

  return (
    <div className="flex flex-col items-center justify-center h-full relative">
      {/* Base platform */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <div className="w-32 h-6 bg-gradient-to-r from-gray-700 via-gray-600 to-gray-700 rounded-full shadow-lg" />
      </div>

      {/* Robot body */}
      <div
        className={`absolute bottom-14 left-1/2 -translate-x-1/2 transition-all duration-700 ${
          isMoving ? 'animate-pulse' : ''
        }`}
        style={{ transformOrigin: 'bottom center' }}
      >
        {/* Body */}
        <div className="w-16 h-20 bg-gradient-to-b from-gray-500 to-gray-700 rounded-lg mx-auto relative border border-gray-500 shadow-xl">
          {/* Eyes */}
          <div className="flex gap-2 justify-center pt-3">
            <div
              className={`w-3 h-3 rounded-full ${
                isMoving ? 'bg-orange-400 animate-ping' : 'bg-blue-400'
              }`}
            />
            <div
              className={`w-3 h-3 rounded-full ${
                isMoving ? 'bg-orange-400 animate-ping' : 'bg-blue-400'
              }`}
            />
          </div>
          {/* Chest panel */}
          <div className="mx-3 mt-2 h-6 bg-gray-800 rounded flex items-center justify-center">
            <div
              className={`w-2 h-2 rounded-full ${
                state === 'done' ? 'bg-green-400' : isMoving ? 'bg-orange-400' : 'bg-gray-500'
              }`}
            />
          </div>
        </div>

        {/* Arm */}
        <div
          className="absolute -right-8 top-2 w-14 h-4 bg-gradient-to-r from-gray-500 to-gray-400 rounded-full origin-left transition-transform duration-700 shadow-lg"
          style={{ transform: `rotate(${armAngle}deg)` }}
        >
          {/* Gripper */}
          <div className="absolute right-0 -top-1 w-5 h-6 flex flex-col gap-1">
            <div
              className={`h-2 w-5 bg-orange-500 rounded transition-all duration-300 ${
                state === 'pick' ? 'translate-y-1' : ''
              }`}
            />
            <div
              className={`h-2 w-5 bg-orange-500 rounded transition-all duration-300 ${
                state === 'pick' ? '-translate-y-1' : ''
              }`}
            />
          </div>
        </div>

        {/* Other arm (left, static) */}
        <div className="absolute -left-8 top-2 w-14 h-4 bg-gradient-to-l from-gray-500 to-gray-400 rounded-full shadow-lg" />
      </div>

      {/* State label */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 text-xs text-gray-400 uppercase tracking-widest">
        {{
          idle: '● STANDBY',
          navigate: '▶ NAVIGATING',
          pick: '⊕ PICKING',
          return: '◀ RETURNING',
          done: '✓ COMPLETE',
        }[state]}
      </div>
    </div>
  );
}

// ─── Picked Items Box ─────────────────────────────────────────────────────────

function PickedItemCard({ item, index }: { item: PickedItem; index: number }) {
  return (
    <div
      className="flex items-center gap-2 bg-gray-800 rounded-lg p-2 border border-orange-500/30 animate-fadeIn"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="w-10 h-10 rounded overflow-hidden bg-gray-700 flex-shrink-0">
        {item.imageUrl ? (
          <img src={item.imageUrl} alt={item.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-lg">👗</div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-xs text-orange-400 font-semibold truncate">{item.brand}</div>
        <div className="text-xs text-gray-300 truncate">{item.name}</div>
      </div>
      <div className="text-xs text-white font-mono">${item.price?.toLocaleString()}</div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function DemoPage() {
  const [events, setEvents] = useState<DemoEvent[]>([]);
  const [pickedItems, setPickedItems] = useState<PickedItem[]>([]);
  const [robotState, setRobotState] = useState<RobotState>('idle');
  const [demoRunning, setDemoRunning] = useState(false);
  const [connected, setConnected] = useState(false);
  const [trackingSteps, setTrackingSteps] = useState<TrackingStep[]>([]);
  const [orderTotal, setOrderTotal] = useState(0);
  const [dispatchStatus, setDispatchStatus] = useState('');

  const feedRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const eventIdRef = useRef(0);

  const addEvent = useCallback((evt: Omit<DemoEvent, 'id'>) => {
    const id = `evt-${++eventIdRef.current}`;
    setEvents((prev) => [...prev, { ...evt, id }]);
  }, []);

  // Auto-scroll feed
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [events]);

  // WebSocket connection
  const connectWS = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (msg) => {
      try {
        const evt = JSON.parse(msg.data) as Omit<DemoEvent, 'id'>;
        addEvent(evt);

        // Update robot state from robot events
        if (evt.type === 'robot') {
          const step = (evt.data as { step?: string })?.step;
          if (step === 'navigate') setRobotState('navigate');
          else if (step === 'pick') setRobotState('pick');
          else if (step === 'return') setRobotState('return');
        }

        // Collect picked items
        if (evt.type === 'robot' && (evt.data as { item?: PickedItem })?.item) {
          const item = (evt.data as { item: PickedItem }).item;
          setPickedItems((prev) => [...prev, item]);
        }

        // Dispatch tracking
        if (evt.type === 'dispatch') {
          const steps = (evt.data as { tracking_steps?: TrackingStep[] })?.tracking_steps;
          if (steps) setTrackingSteps(steps);
          const total = (evt.data as { total?: number })?.total;
          if (total) setOrderTotal(total);
          setDispatchStatus(evt.message);
        }

        // Complete
        if (evt.type === 'complete') {
          setRobotState('done');
          setDemoRunning(false);
          const total = (evt.data as { total?: number })?.total;
          if (total) setOrderTotal(total);
        }

        if (evt.type === 'error') {
          setDemoRunning(false);
        }
      } catch {
        // ignore parse errors
      }
    };
  }, [addEvent]);

  useEffect(() => {
    connectWS();
    return () => wsRef.current?.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRunDemo = async () => {
    if (demoRunning) return;

    // Reset state
    setEvents([]);
    setPickedItems([]);
    setRobotState('idle');
    setTrackingSteps([]);
    setOrderTotal(0);
    setDispatchStatus('');
    setDemoRunning(true);

    // Reconnect WS if needed
    connectWS();

    try {
      await fetch(`${API_URL}/api/demo/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: 'demo_customer_001',
          ...DEMO_CUSTOMER,
        }),
      });
    } catch (err) {
      console.error('Demo start error:', err);
      setDemoRunning(false);
    }
  };

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
          {/* WS status */}
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            {connected ? 'Connected' : 'Disconnected'}
          </div>

          <button
            onClick={handleRunDemo}
            disabled={demoRunning}
            className={`px-5 py-2 rounded-lg font-semibold text-sm transition-all ${
              demoRunning
                ? 'bg-orange-500/30 text-orange-300 cursor-not-allowed'
                : 'bg-orange-500 hover:bg-orange-400 text-white shadow-lg shadow-orange-500/20 hover:shadow-orange-500/40'
            }`}
          >
            {demoRunning ? '⟳ Running…' : '▶ Run Demo'}
          </button>
        </div>
      </header>

      {/* ── Three-panel layout ── */}
      <div className="flex flex-1 overflow-hidden">
        {/* ── LEFT: Agent Activity Feed ── */}
        <div className="w-72 border-r border-gray-800 flex flex-col flex-shrink-0">
          <div className="px-4 py-3 border-b border-gray-800">
            <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Agent Activity</div>
          </div>
          <div ref={feedRef} className="flex-1 overflow-y-auto p-3 space-y-2">
            {events.length === 0 ? (
              <div className="text-gray-600 text-xs text-center mt-8">
                Press &ldquo;Run Demo&rdquo; to start
              </div>
            ) : (
              events.map((evt) => (
                <div
                  key={evt.id}
                  className={`border-l-2 pl-3 py-1.5 ${EVENT_COLORS[evt.type]}`}
                >
                  <div className="text-xs leading-snug">
                    <span className="mr-1">{EVENT_ICONS[evt.type]}</span>
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

        {/* ── CENTER: Robot Visualization ── */}
        <div className="flex-1 flex flex-col border-r border-gray-800 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-800">
            <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Robot Visualization</div>
          </div>

          <div className="flex-1 relative overflow-hidden">
            {/* Robot arm animation */}
            <div className="h-2/3 relative">
              <RobotArm state={robotState} />

              {/* Grid floor */}
              <div
                className="absolute bottom-0 left-0 right-0 h-12 opacity-10"
                style={{
                  backgroundImage: 'repeating-linear-gradient(90deg, #FF6B00 0px, transparent 1px, transparent 40px)',
                }}
              />
            </div>

            {/* Picked items box */}
            <div className="h-1/3 border-t border-gray-800 px-4 py-3">
              <div className="text-xs text-gray-500 uppercase tracking-widest mb-2 font-semibold">
                Dispatch Box {pickedItems.length > 0 && `(${pickedItems.length} items)`}
              </div>
              <div className="space-y-1.5 overflow-y-auto max-h-full">
                {pickedItems.length === 0 ? (
                  <div className="text-gray-700 text-xs">No items picked yet</div>
                ) : (
                  pickedItems.map((item, i) => (
                    <PickedItemCard key={`${item.sku}-${i}`} item={item} index={i} />
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ── RIGHT: Order Summary ── */}
        <div className="w-80 flex flex-col flex-shrink-0">
          <div className="px-4 py-3 border-b border-gray-800">
            <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Order Summary</div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Customer profile */}
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-full bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-lg">
                  👤
                </div>
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
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Sizes</span>
                  <span className="text-white">Tops: {DEMO_CUSTOMER.sizes.tops}, Bottoms: {DEMO_CUSTOMER.sizes.bottoms}</span>
                </div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {DEMO_CUSTOMER.style_tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-gray-800 text-gray-400 rounded text-xs border border-gray-700">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-1 mt-1">
                  {DEMO_CUSTOMER.preferred_brands.map((b) => (
                    <span key={b} className="px-2 py-0.5 bg-orange-500/10 text-orange-400 rounded text-xs border border-orange-500/20">
                      {b}
                    </span>
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
                          <img src={item.imageUrl} alt={item.name} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-xl">🛍️</div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs text-orange-400 font-semibold">{item.brand}</div>
                        <div className="text-xs text-gray-300 truncate">{item.name}</div>
                        <div className="text-sm font-mono text-white mt-0.5">
                          ${item.price?.toLocaleString() ?? '—'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Running total */}
                <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-800">
                  <span className="text-gray-400 text-sm">Total</span>
                  <span className="text-white font-bold font-mono text-lg">
                    ${(orderTotal || pickedItems.reduce((s, i) => s + (i.price ?? 0), 0)).toLocaleString()}
                  </span>
                </div>
              </div>
            )}

            {/* Dispatch tracking */}
            {trackingSteps.length > 0 && (
              <div>
                <div className="text-xs text-gray-500 uppercase tracking-widest mb-3 font-semibold">Dispatch Status</div>
                {dispatchStatus && (
                  <div className="text-xs text-green-400 mb-3 bg-green-500/10 border border-green-500/20 rounded-lg px-3 py-2">
                    {dispatchStatus}
                  </div>
                )}
                <div className="relative">
                  <div className="absolute left-3 top-3 bottom-3 w-px bg-gray-800" />
                  <div className="space-y-3">
                    {trackingSteps.map((step, i) => (
                      <div key={i} className="flex items-center gap-3 pl-1">
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 z-10 text-xs ${
                            step.done
                              ? 'bg-green-500 text-white'
                              : 'bg-gray-800 border border-gray-700 text-gray-600'
                          }`}
                        >
                          {step.done ? '✓' : i + 1}
                        </div>
                        <span
                          className={`text-sm ${step.done ? 'text-white' : 'text-gray-600'}`}
                        >
                          {step.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {events.some((e) => e.type === 'complete') && (
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 text-center">
                <div className="text-2xl mb-1">🎉</div>
                <div className="text-emerald-300 font-semibold text-sm">Demo Complete!</div>
                <div className="text-gray-400 text-xs mt-1">
                  Style.re delivery on the way for {DEMO_CUSTOMER.name}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
