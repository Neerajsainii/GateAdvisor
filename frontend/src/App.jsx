import { AnimatePresence, motion } from "framer-motion";
import { useCallback, useEffect, useMemo, useState } from "react";

import { api, loadRazorpayScript, setAuthToken } from "./lib/api";

const fallbackMetadata = {
  branches: [
    { value: "CS", label: "Computer Science" },
    { value: "ME", label: "Mechanical" },
    { value: "EE", label: "Electrical" },
    { value: "EC", label: "Electronics" },
    { value: "CE", label: "Civil" },
    { value: "CH", label: "Chemical" },
  ],
  categories: [
    { value: "GENERAL", label: "General" },
    { value: "GENERAL_PWD", label: "General PwD" },
    { value: "OBC_NCL", label: "OBC-NCL" },
    { value: "OBC_NCL_PWD", label: "OBC-NCL PwD" },
    { value: "SC", label: "SC" },
    { value: "SC_PWD", label: "SC PwD" },
    { value: "ST", label: "ST" },
    { value: "ST_PWD", label: "ST PwD" },
    { value: "EWS", label: "EWS" },
    { value: "EWS_PWD", label: "EWS PwD" },
  ],
  unlock_amount: 1000,
  razorpay_key_id: "",
  subscription_plans: [
    {
      code: "weekly",
      title: "Weekly Pass",
      subtitle: "Quick shortlist access",
      duration_label: "7 days access",
      amount_paise: 1000,
      original_amount_paise: 10000,
      display_amount: 10,
      display_original_amount: 100,
      discount_label: "90% OFF",
      recommended: false,
    },
    {
      code: "monthly",
      title: "Monthly Pass",
      subtitle: "Steady prep companion",
      duration_label: "30 days access",
      amount_paise: 4900,
      original_amount_paise: 4900,
      display_amount: 49,
      display_original_amount: 49,
      discount_label: "",
      recommended: false,
    },
    {
      code: "yearly",
      title: "Yearly Pass",
      subtitle: "Best value for full prep",
      duration_label: "365 days access",
      amount_paise: 9900,
      original_amount_paise: 99900,
      display_amount: 99,
      display_original_amount: 999,
      discount_label: "90% OFF",
      recommended: true,
    },
  ],
};

const contactProfile = {
  owner: "Neeraj Saini",
  email: "sainineeraj123789@gmail.com",
  instagram: "@mei.neeru",
  linkedin: "linkedin.com/in/neeraj-saini-414546310/",
  github: "github.com/Neerajsainii",
};

const infoPageLinks = [
  { label: "Privacy Policy", href: "/?page=privacy-policy", path: "/privacy-policy" },
  { label: "Terms & Conditions", href: "/?page=terms-and-conditions", path: "/terms-and-conditions" },
  { label: "Contact Us", href: "/?page=contact-us", path: "/contact-us" },
  { label: "Refund Policy", href: "/?page=refund-policy", path: "/refund-policy" },
];

const infoPages = {
  "/privacy-policy": {
    title: "Privacy Policy",
    subtitle: "How we collect, use, and protect your data on GATE Advisor.",
    sections: [
      {
        heading: "Data We Collect",
        body: "We may collect your GATE score, branch, category, optional rank, email, account details, and payment reference data required to deliver your results and unlock access.",
      },
      {
        heading: "How Data Is Used",
        body: "Your data is used to generate eligibility predictions, personalize recommendations, manage account access, and support payment verification and customer support.",
      },
      {
        heading: "Data Sharing",
        body: "We do not sell your personal data. Payment processing is handled through Razorpay and only necessary payment metadata is stored for order verification and transaction records.",
      },
      {
        heading: "Retention & Security",
        body: "We retain data only as needed for product usage, analytics, and legal compliance. Reasonable technical and operational safeguards are used to protect stored information.",
      },
      {
        heading: "Your Controls",
        body: "You can contact us to request profile updates or account-related support. For privacy concerns, reach us directly via the email listed on the Contact Us page.",
      },
    ],
  },
  "/terms-and-conditions": {
    title: "Terms & Conditions",
    subtitle: "Terms for using GATE Advisor services and paid unlock features.",
    sections: [
      {
        heading: "Service Scope",
        body: "GATE Advisor provides decision-support insights based on historical cutoff data and configured matching logic. Results are advisory and do not guarantee admission.",
      },
      {
        heading: "User Responsibility",
        body: "Users are responsible for entering accurate details. Incorrect or incomplete information may lead to inaccurate predictions and recommendations.",
      },
      {
        heading: "Payments and Access",
        body: "Paid plans unlock enhanced results for the selected duration. Access is intended for personal use only and must not be resold, shared, or redistributed.",
      },
      {
        heading: "Acceptable Use",
        body: "You agree not to abuse, scrape, reverse engineer, or disrupt platform operations. Fraudulent payment activity may result in access suspension.",
      },
      {
        heading: "Liability Limitation",
        body: "The platform is provided on an as-is basis. We are not liable for admission outcomes, third-party counseling decisions, or losses caused by external systems.",
      },
    ],
  },
  "/refund-policy": {
    title: "Refund Policy",
    subtitle: "Policy for payment disputes, duplicate charges, and refund requests.",
    sections: [
      {
        heading: "Digital Service Nature",
        body: "GATE Advisor provides instant digital access to paid insights. Because benefits are delivered immediately, completed unlocks are generally non-refundable.",
      },
      {
        heading: "Eligible Refund Cases",
        body: "Refunds may be considered for duplicate payments or technically failed transactions where amount is captured but access is not granted.",
      },
      {
        heading: "Request Window",
        body: "Refund requests should be raised within 7 calendar days of transaction date with payment reference details for verification.",
      },
      {
        heading: "Processing Timeline",
        body: "Once approved, refunds are initiated to the original payment method. Bank/card/network processing can take 5 to 7 business days.",
      },
      {
        heading: "Support Contact",
        body: "For refund help, use the email in Contact Us with your order ID, payment ID, date, and registered email.",
      },
    ],
  },
  "/contact-us": {
    title: "Contact Us",
    subtitle: "Reach out for support, refunds, or freelance full-stack project inquiries.",
    sections: [
      {
        heading: "General Support",
        body: "For product issues, account access, result mismatch reports, or payment verification support, contact us through email.",
      },
      {
        heading: "Freelance Projects",
        body: "Need a similar product, dashboard, automation, or payment integration for your business or startup? Contact us to discuss scope, timeline, and commercials.",
      },
      {
        heading: "Response SLA",
        body: "We generally respond within 24 to 48 hours on business days.",
      },
    ],
  },
};

function formatRupees(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

const defaultForm = {
  gate_score: "",
  branch: "CS",
  category: "GENERAL",
  include_interdisciplinary: true,
  rank: "",
  email: "",
};

const defaultFilters = { institute: "All", probability: "All", branch: "All", matchType: "All" };
const defaultAuthForm = { full_name: "", email: "", password: "" };
const storageKeys = {
  form: "gate_advisor_form",
  filters: "gate_advisor_filters",
  results: "gate_advisor_results",
  user: "gate_advisor_user",
};

function readStoredJson(key, fallback) {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function writeStoredJson(key, value) {
  if (typeof window === "undefined") {
    return;
  }
  if (value === null || value === undefined) {
    window.localStorage.removeItem(key);
    return;
  }
  window.localStorage.setItem(key, JSON.stringify(value));
}

const steps = [
  { title: "Enter details", body: "Add score, GATE paper, category, and optional rank." },
  { title: "See eligible IITs", body: "Get a free preview with best-fit programs." },
  { title: "Unlock full insights", body: "Pay Rs 10 for the complete ranked list and guidance." },
];

const probabilityTone = {
  High: "text-emerald-200 bg-emerald-400/15 border-emerald-300/30",
  Medium: "text-amber-100 bg-amber-400/15 border-amber-200/30",
  Low: "text-sky-100 bg-sky-400/15 border-sky-200/30",
  Reach: "text-rose-100 bg-rose-400/15 border-rose-200/30",
  "Marks-based": "text-violet-100 bg-violet-400/15 border-violet-200/30",
};

function App() {
  const pathname =
    typeof window !== "undefined"
      ? ((window.location.pathname || "/").replace(/\/+$/, "") || "/").toLowerCase()
      : "/";
  const queryPage =
    typeof window !== "undefined"
      ? (new window.URLSearchParams(window.location.search).get("page") || "").toLowerCase()
      : "";
  const queryPath = queryPage ? `/${queryPage.replace(/^\/+/, "")}` : "";
  const activeInfoPage = infoPages[pathname] || infoPages[queryPath] || null;
  const restoredResultState = readStoredJson(storageKeys.results, null);
  const [metadata, setMetadata] = useState(fallbackMetadata);
  const [form, setForm] = useState(() => ({ ...defaultForm, ...readStoredJson(storageKeys.form, {}) }));
  const [resultState, setResultState] = useState(() => restoredResultState);
  const [loading, setLoading] = useState(false);
  const [unlocking, setUnlocking] = useState(false);
  const [showPlans, setShowPlans] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState(defaultAuthForm);
  const [authLoading, setAuthLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState(() => readStoredJson(storageKeys.user, null));
  const [error, setError] = useState("");
  const [authError, setAuthError] = useState("");
  const [filters, setFilters] = useState(() => ({ ...defaultFilters, ...readStoredJson(storageKeys.filters, {}) }));
  const [restoredAttemptId] = useState(() => restoredResultState?.attempt?.id || null);

  const refreshResults = useCallback(async (attemptId) => {
    const response = await api.get(`/results/${attemptId}/`);
    setResultState(response.data);
  }, []);

  useEffect(() => {
    if (activeInfoPage) {
      return;
    }
    api.get("/metadata/").then((response) => setMetadata(response.data)).catch(() => setMetadata(fallbackMetadata));
  }, [activeInfoPage]);

  useEffect(() => {
    if (activeInfoPage) {
      return;
    }
    api.get("/auth/me/")
      .then((response) => {
        setCurrentUser(response.data.user);
        setForm((current) => ({ ...current, email: current.email || response.data.user.email || "" }));
      })
      .catch(() => {
        setAuthToken("");
        setCurrentUser(null);
      });
  }, [activeInfoPage]);

  useEffect(() => {
    if (activeInfoPage) {
      return;
    }
    if (restoredAttemptId) {
      refreshResults(restoredAttemptId).catch(() => null);
    }
  }, [activeInfoPage, refreshResults, restoredAttemptId]);

  useEffect(() => {
    writeStoredJson(storageKeys.form, form);
  }, [form]);

  useEffect(() => {
    writeStoredJson(storageKeys.filters, filters);
  }, [filters]);

  useEffect(() => {
    writeStoredJson(storageKeys.results, resultState);
  }, [resultState]);

  useEffect(() => {
    writeStoredJson(storageKeys.user, currentUser);
  }, [currentUser]);

  const allResults = useMemo(() => resultState?.results || [], [resultState]);
  const institutes = useMemo(
    () => ["All", ...Array.from(new Set(allResults.map((result) => result.acronym)))],
    [allResults],
  );

  const filteredResults = useMemo(() => {
    return allResults.filter((result) => {
      const instituteMatch = filters.institute === "All" || result.acronym === filters.institute;
      const probabilityMatch =
        filters.probability === "All" || result.admission_probability === filters.probability;
      const branchMatch = filters.branch === "All" || result.branch === filters.branch;
      const matchTypeMatch = filters.matchType === "All" || result.match_type === filters.matchType;
      return instituteMatch && probabilityMatch && branchMatch && matchTypeMatch;
    });
  }, [allResults, filters]);

  async function submitPreview(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        gate_score: Number(form.gate_score),
        branch: form.branch,
        category: form.category,
        include_interdisciplinary: form.include_interdisciplinary,
        email: form.email,
      };
      if (form.rank) {
        payload.rank = Number(form.rank);
      }
      const response = await api.post("/results/preview/", payload);
      setResultState(response.data);
      document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Could not generate results. Please check your inputs.");
    } finally {
      setLoading(false);
    }
  }

  function openPlans() {
    if (!resultState?.attempt?.id) {
      setError("Please generate a preview before unlocking.");
      return;
    }
    if (!currentUser) {
      setAuthMode("login");
      setAuthError("");
      setShowAuthModal(true);
      return;
    }
    setShowPlans(true);
  }

  
  async function submitAuth(event) {
    event.preventDefault();
    setAuthError("");
    setAuthLoading(true);
    try {
      const endpoint = authMode === "signup" ? "/auth/signup/" : "/auth/login/";
      const payload =
        authMode === "signup"
          ? authForm
          : { email: authForm.email, password: authForm.password };
const response = await api.post(endpoint, payload);

// ✅ STEP 2: Save token in localStorage
localStorage.setItem("token", response.data.token);

// ✅ STEP 3: Update axios immediately
api.defaults.headers.Authorization = `Token ${response.data.token}`;

setAuthToken(response.data.token);
setCurrentUser(response.data.user);
      setForm((current) => ({ ...current, email: current.email || response.data.user.email || "" }));
      setShowAuthModal(false);
      setShowPlans(true);
      setAuthForm((current) => ({ ...defaultAuthForm, email: current.email }));
    } catch (requestError) {
      const responseError = requestError.response?.data;
      if (typeof responseError === "string") {
        setAuthError(responseError);
      } else if (responseError?.non_field_errors?.length) {
        setAuthError(responseError.non_field_errors[0]);
      } else if (responseError?.email?.length) {
        setAuthError(responseError.email[0]);
      } else {
        setAuthError("Could not complete authentication.");
      }
    } finally {
      setAuthLoading(false);
    }
  }

  async function logout() {
    try {
      await api.post("/auth/logout/");
    } catch {
      // Ignore logout transport failures and clear local auth anyway.
    }
    setAuthToken("");
    setCurrentUser(null);
    setShowPlans(false);
  }

  async function unlockResults(planCode) {
    setError("");
    setUnlocking(true);
    try {
      const orderResponse = await api.post("/payments/create-order/", {
        attempt_id: resultState.attempt.id,
        plan_code: planCode,
      });
      const order = orderResponse.data.order;

      if (order.development_mode || !order.key_id) {
        await api.post("/payments/verify/", {
          attempt_id: resultState.attempt.id,
          razorpay_order_id: order.id,
          razorpay_payment_id: "pay_mock_development",
          razorpay_signature: "debug",
        });
        await refreshResults(resultState.attempt.id);
        setShowPlans(false);
        return;
      }

      const canUseRazorpay = await loadRazorpayScript();
      if (!canUseRazorpay) {
        throw new Error("Razorpay checkout could not be loaded.");
      }

      const checkout = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "GATE IIT Advisor",
        description: "Unlock full IIT and M.Tech recommendations",
        order_id: order.id,
        prefill: { email: form.email || currentUser?.email || "" },
        theme: { color: "#6d5dfc" },
        handler: async (payment) => {
          await api.post("/payments/verify/", {
            attempt_id: resultState.attempt.id,
            razorpay_order_id: payment.razorpay_order_id,
            razorpay_payment_id: payment.razorpay_payment_id,
            razorpay_signature: payment.razorpay_signature,
          });
          await refreshResults(resultState.attempt.id);
          setShowPlans(false);
        },
      });
      checkout.open();
    } catch (unlockError) {
      if (unlockError.response?.status === 401) {
        setShowPlans(false);
        setShowAuthModal(true);
      }
      setError(unlockError.response?.data?.message || unlockError.message || "Payment could not be completed.");
    } finally {
      setUnlocking(false);
    }
  }

  if (activeInfoPage) {
    return <InfoPage page={activeInfoPage} />;
  }
  return (
    <main className="min-h-screen overflow-hidden bg-[#07111f] text-white">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <section className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-6 sm:px-8 lg:px-10">
        <nav className="glass-panel flex items-center justify-between rounded-full px-5 py-3">
          <span className="text-sm font-semibold tracking-[0.32em] text-cyan-100">GATE ADVISOR</span>
          <div className="flex items-center gap-3">
            {currentUser ? (
              <>
                <div className="hidden text-right sm:block">
                  <div className="text-sm font-medium text-white">{currentUser.full_name}</div>
                  <div className="text-xs text-slate-300/70">{currentUser.email}</div>
                </div>
                <button onClick={logout} className="secondary-button">
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => {
                    setAuthMode("login");
                    setAuthError("");
                    setShowAuthModal(true);
                  }}
                  className="secondary-button"
                >
                  Login
                </button>
                <button
                  onClick={() => {
                    setAuthMode("signup");
                    setAuthError("");
                    setShowAuthModal(true);
                  }}
                  className="primary-button"
                >
                  Sign Up
                </button>
              </>
            )}
            <a href="#results" className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80">
              Dashboard
            </a>
          </div>
        </nav>

        <div className="grid flex-1 items-center gap-8 py-14 lg:grid-cols-[1.05fr_0.95fr]">
          <Hero onStart={() => document.getElementById("checker")?.scrollIntoView({ behavior: "smooth" })} />
          <CheckerCard
            metadata={metadata}
            form={form}
            setForm={setForm}
            loading={loading}
            onSubmit={submitPreview}
            error={error}
          />
        </div>
      </section>

      <section id="results" className="relative mx-auto max-w-7xl px-5 pb-24 sm:px-8 lg:px-10">
        <ResultsSection
          metadata={metadata}
          resultState={resultState}
          filteredResults={filteredResults}
          institutes={institutes}
          filters={filters}
          setFilters={setFilters}
          unlocking={unlocking}
          onUnlock={openPlans}
        />
      </section>
      <Footer />
      {showAuthModal ? (
        <AuthModal
          authMode={authMode}
          authForm={authForm}
          authLoading={authLoading}
          authError={authError}
          onChangeMode={(mode) => {
            setAuthMode(mode);
            setAuthError("");
          }}
          onClose={() => {
            setShowAuthModal(false);
            setAuthError("");
          }}
          onFieldChange={(field, value) => setAuthForm((current) => ({ ...current, [field]: value }))}
          onSubmit={submitAuth}
        />
      ) : null}
      {showPlans ? (
        <PlanModal
          plans={metadata.subscription_plans || fallbackMetadata.subscription_plans}
          unlocking={unlocking}
          onClose={() => setShowPlans(false)}
          onSelectPlan={unlockResults}
        />
      ) : null}
    </main>
  );
}

function Hero({ onStart }) {
  return (
    <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
      <div className="mb-5 inline-flex rounded-full border border-cyan-200/20 bg-cyan-200/10 px-4 py-2 text-sm text-cyan-100">
        Decision support for GATE-qualified applicants
      </div>
      <h1 className="max-w-3xl text-3xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-7xl">
        Find the best IIT you can get with your GATE score
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-7 text-slate-200/80 sm:text-lg sm:leading-8">
        Enter your score, branch, and category to see eligible IIT M.Tech programs, indicative cutoffs,
        probability bands, and COAP application guidance in one flow.
      </p>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <button onClick={onStart} className="primary-button">Check Your Chances</button>
        <a href="#guide" className="secondary-button">See how it works</a>
      </div>
      <div id="guide" className="mt-10 grid gap-4 md:grid-cols-3">
        {steps.map((step, index) => (
          <motion.div
            className="glass-panel rounded-3xl p-5"
            key={step.title}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.12 + 0.2 }}
          >
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-2xl bg-white/15 text-sm font-bold">
              {index + 1}
            </div>
            <h3 className="font-semibold">{step.title}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-200/70">{step.body}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

function CheckerCard({ metadata, form, setForm, loading, onSubmit, error }) {
  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  return (
    <motion.form
      id="checker"
      onSubmit={onSubmit}
      className="glass-panel rounded-[2rem] p-5 shadow-glass sm:p-7"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.7, delay: 0.1 }}
    >
      <div className="mb-6">
        <p className="text-sm uppercase tracking-[0.28em] text-cyan-100/80">Step-based checker</p>
        <h2 className="mt-2 text-2xl font-semibold sm:text-3xl">Get your free preview</h2>
        <p className="mt-2 text-sm text-slate-200/70">No login required. Unlock the full list only if it helps.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="field sm:col-span-2">
          <span>GATE score</span>
          <input
            type="number"
            min="0"
            max="1000"
            required
            value={form.gate_score}
            onChange={(event) => updateField("gate_score", event.target.value)}
            placeholder="Example: 760"
          />
        </label>
        <label className="field">
          <span>Branch</span>
          <select value={form.branch} onChange={(event) => updateField("branch", event.target.value)}>
            {metadata.branches.map((branch) => (
              <option value={branch.value} key={branch.value}>{branch.label}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Category</span>
          <select value={form.category} onChange={(event) => updateField("category", event.target.value)}>
            {metadata.categories.map((category) => (
              <option value={category.value} key={category.value}>{category.label}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Rank optional</span>
          <input
            type="number"
            min="1"
            value={form.rank}
            onChange={(event) => updateField("rank", event.target.value)}
            placeholder="Example: 1240"
          />
        </label>
        <label className="field">
          <span>Email optional</span>
          <input
            type="email"
            value={form.email}
            onChange={(event) => updateField("email", event.target.value)}
            placeholder="you@example.com"
          />
        </label>
      </div>

      <label className="mt-5 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-sm text-slate-200/80">
        <input
          type="checkbox"
          checked={form.include_interdisciplinary}
          onChange={(event) => updateField("include_interdisciplinary", event.target.checked)}
        />
        <span>Include interdisciplinary and allied programs too</span>
      </label>

      <button className="primary-button mt-6 w-full justify-center" disabled={loading}>
        {loading ? "Calculating..." : "Check Your Chances"}
      </button>
      <p className="mt-3 text-center text-xs text-slate-300/60">
        Your latest form inputs and preview stay saved on this device even after refresh.
      </p>
      {error ? <p className="mt-4 rounded-2xl border border-rose-300/30 bg-rose-400/10 p-3 text-sm text-rose-100">{error}</p> : null}
    </motion.form>
  );
}

function ResultsSection({
  metadata,
  resultState,
  filteredResults,
  institutes,
  filters,
  setFilters,
  unlocking,
  onUnlock,
}) {
  if (!resultState) {
    return (
      <div className="glass-panel rounded-[2rem] p-8 text-center text-slate-200/75">
        Generate a preview to see IIT matches, cutoff bands, and unlock options here.
      </div>
    );
  }

  const isPaid = resultState.attempt?.is_paid;
  const groupedResults = [
    { label: "Direct Matches", value: "Direct" },
    { label: "Allied Matches", value: "Allied" },
    { label: "Interdisciplinary Matches", value: "Interdisciplinary" },
  ]
    .map((group) => ({
      ...group,
      items: filteredResults.filter((result) => result.match_type === group.value),
    }))
    .filter((group) => group.items.length > 0);

  return (
    <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
      <aside className="glass-panel order-2 h-fit rounded-[2rem] p-5 sm:p-6 lg:order-1">
        <p className="text-sm uppercase tracking-[0.28em] text-cyan-100/80">Dashboard</p>
        <h2 className="mt-2 text-2xl font-semibold sm:text-3xl">
          {isPaid ? "Full ranked results" : "Free preview"}
        </h2>
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <Metric label="Matches" value={resultState.total_matches} />
          <Metric label="Visible" value={resultState.results.length} />
          <Metric label="Locked" value={resultState.locked_count} />
        </div>

        <div className="mt-6 grid gap-3">
          <SelectFilter label="IIT" value={filters.institute} onChange={(value) => setFilters({ ...filters, institute: value })} options={institutes} />
          <SelectFilter label="Probability" value={filters.probability} onChange={(value) => setFilters({ ...filters, probability: value })} options={["All", "High", "Medium", "Low", "Reach", "Marks-based"]} />
          <SelectFilter label="Branch" value={filters.branch} onChange={(value) => setFilters({ ...filters, branch: value })} options={["All", ...metadata.branches.map((branch) => branch.value)]} />
          <SelectFilter label="Match type" value={filters.matchType} onChange={(value) => setFilters({ ...filters, matchType: value })} options={["All", "Direct", "Allied", "Interdisciplinary"]} />
        </div>

        {!isPaid ? (
          <div className="mt-6 hidden rounded-3xl border border-cyan-200/20 bg-cyan-200/10 p-5 lg:block">
            <h3 className="font-semibold">Choose a plan to unlock everything</h3>
            <p className="mt-2 text-sm leading-6 text-slate-200/70">
              Open the plan popup to pick weekly, monthly, or yearly access to full results and guidance.
            </p>
            <button onClick={onUnlock} className="primary-button mt-4 w-full justify-center" disabled={unlocking}>
              {unlocking ? "Opening payment..." : "Unlock Full List"}
            </button>
          </div>
        ) : null}

        <Guidance guidance={resultState.guidance} isPaid={isPaid} />
      </aside>

      <div className="relative order-1 lg:order-2">
        {groupedResults.length > 0 ? (
          <div className="grid gap-6">
            {groupedResults.map((group) => (
              <section key={group.value}>
                <div className="mb-3 text-sm font-semibold uppercase tracking-[0.24em] text-cyan-100/75">{group.label}</div>
                <div className="grid gap-4">
                  <AnimatePresence>
                    {group.items.map((result) => (
                      <ResultCard key={`${group.value}-${result.acronym}-${result.program}`} result={result} />
                    ))}
                  </AnimatePresence>
                </div>
              </section>
            ))}
          </div>
        ) : (
          <div className="glass-panel rounded-[2rem] p-6 text-center text-slate-200/70">
            No results match the current filters.
          </div>
        )}

        {!isPaid && resultState.locked_count > 0 ? (
          <div className="glass-panel mt-4 rounded-[2rem] p-5 text-center sm:p-8">
            <div className="mx-auto mb-4 h-20 max-w-xl rounded-3xl border border-white/10 bg-white/10 blur-sm" />
            <h3 className="text-xl font-semibold sm:text-2xl">More programs are waiting</h3>
            <p className="mt-2 text-sm leading-6 text-slate-200/70 sm:text-base">
              {resultState.locked_count} additional IIT and M.Tech matches are blurred until payment is verified.
            </p>
            <div className="mx-auto mt-5 max-w-md rounded-3xl border border-cyan-200/20 bg-cyan-200/10 p-4 text-left lg:hidden">
              <h4 className="font-semibold text-white">Unlock the full list</h4>
              <p className="mt-2 text-sm leading-6 text-slate-200/75">
                Choose a plan to view all remaining matches, filters, and guidance details.
              </p>
              <button
                onClick={onUnlock}
                className="primary-button mt-4 w-full justify-center"
                disabled={unlocking}
              >
                {unlocking ? "Opening payment..." : "Unlock Full List"}
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/10 p-3 text-center">
      <div className="text-xl font-semibold sm:text-2xl">{value}</div>
      <div className="text-xs uppercase tracking-[0.2em] text-slate-300/70">{label}</div>
    </div>
  );
}

function SelectFilter({ label, value, onChange, options }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option value={option} key={option}>{option}</option>
        ))}
      </select>
    </label>
  );
}

function ResultCard({ result }) {
  return (
    <motion.article
      className="glass-panel rounded-[2rem] p-4 sm:p-6"
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 16 }}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-sm text-cyan-100/75">{result.acronym} - {result.city}</div>
          <h3 className="mt-1 text-xl font-semibold sm:text-2xl">{result.iit}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-200/75 sm:text-base">{result.degree} in {result.program}</p>
          <p className="mt-2 text-sm text-slate-300/70">{result.match_type} match. {result.eligibility_note}</p>
        </div>
        <span className={`rounded-full border px-3 py-2 text-xs sm:px-4 sm:text-sm ${probabilityTone[result.admission_probability] || probabilityTone.Reach}`}>
          {result.admission_probability === "Marks-based" ? "Marks-based cutoff" : `${result.admission_probability} probability`}
        </span>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <Metric label={`Cutoff ${result.cutoff_metric_label || "Score"}`} value={result.expected_cutoff_range} />
        <Metric label="Branch" value={result.branch} />
        <Metric label={`Latest ${result.cutoff_metric_label || "Score"}`} value={result.latest_cutoff} />
      </div>
      <div className="mt-5 rounded-3xl border border-white/10 bg-black/10 p-4">
        <div className="mb-3 text-sm font-semibold text-slate-100">Historical data</div>
        <div className="grid gap-2">
          {result.historical_data?.slice(0, 3).map((row) => (
            <div className="flex items-center justify-between text-sm text-slate-200/75" key={row.year}>
              <span>{row.year}</span>
              <span>{row.min_score}-{row.max_score} {row.metric_type === "marks" ? "marks" : "score"}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.article>
  );
}

function Guidance({ guidance, isPaid }) {
  return (
    <div className={`mt-6 ${isPaid ? "" : "opacity-70"}`}>
      <h3 className="font-semibold">{guidance?.title || "How to apply"}</h3>
      <div className="mt-4 space-y-3">
        {guidance?.steps?.map((step) => (
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4" key={step.label}>
            <div className="font-medium">{step.label}</div>
            <p className="mt-1 text-sm leading-6 text-slate-200/65">{step.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function AuthModal({
  authMode,
  authForm,
  authLoading,
  authError,
  onChangeMode,
  onClose,
  onFieldChange,
  onSubmit,
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#020817]/75 px-5 backdrop-blur-md">
      <form onSubmit={onSubmit} className="glass-panel w-full max-w-xl rounded-[2rem] p-6 sm:p-8">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-cyan-100/80">Account</p>
            <h3 className="mt-2 text-3xl font-semibold">
              {authMode === "signup" ? "Create your account" : "Login to continue"}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-200/70">
              Free preview stays open for everyone. Login is required before payment and full unlock.
            </p>
          </div>
          <button type="button" onClick={onClose} className="secondary-button">
            Close
          </button>
        </div>

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={() => onChangeMode("login")}
            className={authMode === "login" ? "primary-button flex-1" : "secondary-button flex-1"}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => onChangeMode("signup")}
            className={authMode === "signup" ? "primary-button flex-1" : "secondary-button flex-1"}
          >
            Sign Up
          </button>
        </div>

        <div className="mt-6 grid gap-4">
          {authMode === "signup" ? (
            <label className="field">
              <span>Full name</span>
              <input
                type="text"
                required
                value={authForm.full_name}
                onChange={(event) => onFieldChange("full_name", event.target.value)}
                placeholder="Your name"
              />
            </label>
          ) : null}

          <label className="field">
            <span>Email</span>
            <input
              type="email"
              required
              value={authForm.email}
              onChange={(event) => onFieldChange("email", event.target.value)}
              placeholder="you@example.com"
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              required
              minLength="8"
              value={authForm.password}
              onChange={(event) => onFieldChange("password", event.target.value)}
              placeholder="Minimum 8 characters"
            />
          </label>
        </div>

        {authError ? (
          <p className="mt-4 rounded-2xl border border-rose-300/30 bg-rose-400/10 p-3 text-sm text-rose-100">
            {authError}
          </p>
        ) : null}

        <button className="primary-button mt-6 w-full justify-center" disabled={authLoading}>
          {authLoading
            ? "Please wait..."
            : authMode === "signup"
              ? "Create account and continue"
              : "Login and continue"}
        </button>
      </form>
    </div>
  );
}

function PlanModal({ plans, unlocking, onClose, onSelectPlan }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#020817]/75 px-5 backdrop-blur-md">
      <div className="glass-panel w-full max-w-5xl rounded-[2rem] p-6 sm:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-cyan-100/80">Unlock full list</p>
            <h3 className="mt-2 text-3xl font-semibold">Choose your access plan</h3>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-200/70">
              Weekly and yearly plans carry the current discount. Monthly stays at the regular price.
            </p>
          </div>
          <button onClick={onClose} className="secondary-button" disabled={unlocking}>
            Close
          </button>
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.code}
              className={`rounded-[2rem] border p-6 ${
                plan.recommended
                  ? "border-cyan-300/40 bg-cyan-300/10 shadow-[0_20px_70px_rgba(34,211,238,0.12)]"
                  : "border-white/10 bg-white/5"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="text-xl font-semibold">{plan.title}</h4>
                  <p className="mt-1 text-sm text-slate-200/70">{plan.subtitle}</p>
                </div>
                {plan.recommended ? (
                  <span className="rounded-full border border-cyan-200/30 bg-cyan-200/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-100">
                    Best Value
                  </span>
                ) : null}
              </div>

              <div className="mt-6">
                <div className="flex items-end gap-3">
                  <span className="text-4xl font-semibold">{formatRupees(plan.display_amount)}</span>
                  {plan.discount_label ? (
                    <span className="pb-1 text-base text-slate-300/55 line-through">
                      {formatRupees(plan.display_original_amount)}
                    </span>
                  ) : null}
                </div>
                <div className="mt-2 flex items-center gap-3">
                  <span className="text-sm text-slate-200/70">{plan.duration_label}</span>
                  {plan.discount_label ? (
                    <span className="rounded-full border border-emerald-300/25 bg-emerald-300/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-100">
                      {plan.discount_label}
                    </span>
                  ) : null}
                </div>
              </div>

              <ul className="mt-6 space-y-3 text-sm text-slate-200/75">
                <li>Full ranked IIT and M.Tech result list</li>
                <li>Direct, allied, and interdisciplinary visibility</li>
                <li>Guidance timeline and cutoff insights</li>
              </ul>

              <button
                onClick={() => onSelectPlan(plan.code)}
                className="primary-button mt-8 w-full justify-center"
                disabled={unlocking}
              >
                {unlocking ? "Starting payment..." : `Continue with ${plan.title}`}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function InfoPage({ page }) {
  return (
    <main className="min-h-screen overflow-hidden bg-[#07111f] text-white">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <section className="relative mx-auto max-w-5xl px-5 py-8 sm:px-8 lg:px-10">
        <nav className="glass-panel flex items-center justify-between rounded-full px-5 py-3">
          <span className="text-sm font-semibold tracking-[0.32em] text-cyan-100">GATE ADVISOR</span>
          <a href="/" className="secondary-button">
            Back to Home
          </a>
        </nav>

        <div className="glass-panel mt-8 rounded-[2rem] p-6 sm:p-8">
          <h1 className="text-3xl font-semibold sm:text-4xl">{page.title}</h1>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-200/75">{page.subtitle}</p>

          <div className="mt-8 space-y-4">
            {page.sections.map((section) => (
              <div key={section.heading} className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <h2 className="text-lg font-semibold">{section.heading}</h2>
                <p className="mt-2 text-sm leading-7 text-slate-200/75">{section.body}</p>
              </div>
            ))}
          </div>

          {page.title === "Contact Us" ? (
            <div className="mt-8 grid gap-3 text-sm text-slate-200/75 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-slate-300/65">Email</div>
                <a className="mt-2 block font-medium text-cyan-100" href={`mailto:${contactProfile.email}`}>
                  {contactProfile.email}
                </a>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-slate-300/65">Social</div>
                <div className="mt-2 grid gap-1">
                  <span>{contactProfile.instagram}</span>
                  <span>{contactProfile.linkedin}</span>
                  <span>{contactProfile.github}</span>
                </div>
              </div>
            </div>
          ) : null}

          <div className="mt-8 flex flex-wrap gap-3 border-t border-white/10 pt-6">
            {infoPageLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm text-slate-100/85"
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

function Footer() {
  return (
    <footer className="relative mx-auto max-w-7xl px-5 pb-10 sm:px-8 lg:px-10">
      <div className="glass-panel rounded-[2rem] p-6 sm:p-8">
        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-cyan-100/80">Contact me</p>
            <h3 className="mt-2 text-3xl font-semibold">Need a similar project built for you?</h3>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-200/70">
              For freelance product builds, payment integrations, dashboards, or full-stack project work, reach out
              and we can discuss scope, timelines, and pricing directly.
            </p>
          </div>
          <div className="grid gap-3 text-sm text-slate-200/75">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs uppercase tracking-[0.2em] text-slate-300/65">Owner</div>
              <div className="mt-2 font-medium">{contactProfile.owner}</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs uppercase tracking-[0.2em] text-slate-300/65">Email</div>
              <div className="mt-2 font-medium">{contactProfile.email}</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs uppercase tracking-[0.2em] text-slate-300/65">Social</div>
              <div className="mt-2 grid gap-1">
                <span>{contactProfile.instagram}</span>
                <span>{contactProfile.linkedin}</span>
                <span>{contactProfile.github}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-6 flex flex-wrap gap-3 border-t border-white/10 pt-5">
          {infoPageLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm text-slate-100/85"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="mt-5 text-sm text-slate-300/60">
          Copyright {new Date().getFullYear()} {contactProfile.owner}. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default App;
