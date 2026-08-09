import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

interface UserAuth {
  access_token: string;
  token_type: string;
  full_name: string;
  role: string;
}

interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  location: string;
  status: string;
  specs: Record<string, any>;
  photos: { path: string; labels: any }[];
}

export default function App() {
  const [auth, setAuth] = useState<UserAuth | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) throw new Error('Invalid email or password');
      const data = await res.json();
      setAuth(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchProperties = async () => {
    if (!auth) return;
    try {
      const res = await fetch(`${API_BASE}/properties`, {
        headers: { Authorization: `Bearer ${auth.access_token}` },
      });
      if (!res.ok) throw new Error('Failed to load listings');
      const data = await res.json();
      setProperties(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    if (auth) {
      fetchProperties();
    }
  }, [auth]);

  if (!auth) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-slate-800 rounded-xl shadow-xl p-8 border border-slate-700">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-extrabold text-white tracking-tight">PropAI</h1>
            <p className="text-slate-400 text-sm mt-1">Prolov · Jawa Barat Property Agent Console</p>
          </div>
          {error && (
            <div className="mb-4 p-3 bg-red-900/50 border border-red-700 text-red-200 rounded-lg text-sm">
              {error}
            </div>
          )}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                placeholder="agent@seed.local"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg transition-colors shadow-lg shadow-indigo-600/30 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="bg-slate-800 border-b border-slate-700 px-8 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span>🏠 PropAI Dashboard</span>
          </h1>
          <p className="text-xs text-slate-400">{auth.full_name} · <span className="uppercase text-indigo-400 font-semibold">{auth.role}</span></p>
        </div>
        <button
          onClick={() => setAuth(null)}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm font-medium rounded-lg transition-colors"
        >
          Sign Out
        </button>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-white">Listings Visible To You</h2>
            <p className="text-sm text-slate-400">Enforced by RBAC query layer</p>
          </div>
          <span className="px-3 py-1 bg-indigo-900/50 border border-indigo-700 text-indigo-300 text-sm font-semibold rounded-full">
            Total: {properties.length}
          </span>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-700 text-red-200 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((p) => {
            const formattedPrice = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(Number(p.price));
            return (
              <div key={p.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <span className="px-2.5 py-0.5 bg-emerald-900/50 border border-emerald-700 text-emerald-300 text-xs font-medium rounded">
                      {p.status}
                    </span>
                    <span className="text-xs text-slate-400">{p.location}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{p.title}</h3>
                  {p.photos?.length > 0 && (
                    <div className="mb-4">
                      {(() => {
                        try {
                          const rawPath = p.photos[0].path;
                          const pathData = typeof rawPath === 'string' ? JSON.parse(rawPath) : rawPath;
                          const imgUrl = `http://localhost:8000${pathData.feature_image}`;
                          return (
                            <img 
                              src={imgUrl} 
                              alt={p.title}
                              className="w-full h-48 object-cover rounded-lg"
                            />
                          );
                        } catch (e) {
                          return <div className="text-xs text-red-500">Image Parse Error</div>;
                        }
                      })()}
                    </div>
                  )}
                  <p className="text-indigo-400 font-semibold text-lg mb-4">{formattedPrice}</p>
                  <p className="text-slate-300 text-sm mb-4 line-clamp-3">{p.description || 'No description provided.'}</p>
                </div>
                <div className="border-t border-slate-700 pt-4 mt-2">
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Specifications</h4>
                  <div className="bg-slate-900 p-3 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto">
                    {JSON.stringify(p.specs, null, 2)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
