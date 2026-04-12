import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, setAuthToken, AUTH_TOKEN_STORAGE_KEY } from "./lib/api";

function AdminBrandLogo() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-blue-500 font-bold text-white shadow-lg">
        G
      </div>
      <div className="font-semibold tracking-wide text-white">GATE Advisor Admin</div>
    </div>
  );
}

export default function AdminApp() {
  const [token, setToken] = useState(() => {
    if (typeof window !== "undefined") {
      return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || "";
    }
    return "";
  });
  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [users, setUsers] = useState([]);
  const [fetchingUsers, setFetchingUsers] = useState(false);

  const handleLogout = useCallback(() => {
    setToken("");
    setAuthToken("");
    setUsers([]);
  }, []);

  const fetchUsers = useCallback(async () => {
    setFetchingUsers(true);
    try {
      const response = await api.get("/admin/users/");
      setUsers(response.data.users);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        handleLogout(); 
      } else {
        setError("Failed to fetch users.");
      }
    } finally {
      setFetchingUsers(false);
    }
  }, [handleLogout]);

  useEffect(() => {
    setAuthToken(token);
    if (token) {
      fetchUsers();
    }
  }, [token, fetchUsers]);

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await api.post("/auth/admin-login/", { username, password });
      setToken(response.data.token);
    } catch (err) {
      setError(err.response?.data?.non_field_errors?.[0] || err.response?.data?.username?.[0] || "Login failed. Check credentials.");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <main className="flex min-h-screen items-center justify-center overflow-hidden bg-[#07111f] p-4 text-white">
        <div className="ambient ambient-one" />
        <div className="ambient ambient-two" />
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative w-full max-w-md"
        >
          <div className="glass-panel overflow-hidden rounded-[2rem] p-8">
            <div className="mb-8 flex justify-center">
              <AdminBrandLogo />
            </div>
            
            <form onSubmit={handleLogin} className="flex flex-col gap-5">
              <div>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-widest text-cyan-200/80">
                  Admin ID
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
                  required
                />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-widest text-cyan-200/80">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
                  required
                />
              </div>
              
              {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                  {error}
                </div>
              )}
              
              <button 
                type="submit" 
                disabled={loading}
                className="rounded-full bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-900 shadow-[0_0_20px_rgba(34,211,238,0.25)] transition hover:bg-cyan-300 hover:shadow-[0_0_25px_rgba(34,211,238,0.35)] mt-4 w-full"
              >
                {loading ? "Authenticating..." : "Login to Console"}
              </button>
            </form>
          </div>
        </motion.div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#07111f] text-white">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      
      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-6 sm:px-8 lg:px-10">
        <nav className="glass-panel flex items-center justify-between rounded-full px-5 py-3">
          <AdminBrandLogo />
          <button 
            onClick={handleLogout} 
            className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 transition hover:bg-white/10"
          >
            Logout
          </button>
        </nav>

        <div className="mt-10 flex-1">
          <div className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white">Users Dashboard</h1>
              <p className="mt-2 text-sm text-slate-300">Overview of all registered users and active subscriptions.</p>
            </div>
            {error && (
              <div className="text-sm text-red-400">
                {error}
              </div>
            )}
            <button 
              onClick={fetchUsers} 
              disabled={fetchingUsers}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-medium uppercase tracking-widest text-cyan-200/80 transition hover:bg-white/10 shrink-0"
            >
              {fetchingUsers ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          <div className="glass-panel overflow-hidden rounded-[2rem]">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="border-b border-white/10 bg-white/5">
                  <tr>
                    <th className="px-6 py-4 font-semibold uppercase tracking-wider text-cyan-200/80 text-xs">User</th>
                    <th className="px-6 py-4 font-semibold uppercase tracking-wider text-cyan-200/80 text-xs">Email</th>
                    <th className="px-6 py-4 font-semibold uppercase tracking-wider text-cyan-200/80 text-xs text-center">Subscribed</th>
                    <th className="px-6 py-4 font-semibold uppercase tracking-wider text-cyan-200/80 text-xs text-center">Plan Type</th>
                    <th className="px-6 py-4 font-semibold uppercase tracking-wider text-cyan-200/80 text-xs text-center">Access Remaining</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  <AnimatePresence>
                    {users.map((user) => (
                      <motion.tr 
                        key={user.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="transition hover:bg-white/5"
                      >
                        <td className="px-6 py-4 font-medium text-white">{user.full_name}</td>
                        <td className="px-6 py-4 text-slate-300">{user.email}</td>
                        <td className="px-6 py-4 text-center">
                          {user.has_subscription === "Yes" ? (
                            <span className="inline-flex rounded-full bg-emerald-400/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400 border border-emerald-400/20">
                              Yes
                            </span>
                          ) : (
                            <span className="inline-flex rounded-full bg-slate-400/10 px-2.5 py-0.5 text-xs font-medium text-slate-400 border border-slate-400/20">
                              No
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={user.subscription_type !== "None" ? "text-cyan-200" : "text-slate-500"}>
                            {user.subscription_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={user.duration_remaining ? "font-medium text-white" : "text-slate-500"}>
                            {user.duration_remaining || "-"}
                          </span>
                        </td>
                      </motion.tr>
                    ))}
                  </AnimatePresence>
                  
                  {!fetchingUsers && users.length === 0 && (
                    <tr>
                      <td colSpan="5" className="px-6 py-12 text-center text-slate-400">
                        No users found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
