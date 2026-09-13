import { useState, useEffect } from 'react';
import { useAuth } from '../providers/AuthProvider';
import { apiClient } from '../api/client';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Skeleton } from '../components/ui/skeleton';
import { Switch } from '../components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  User,
  Bell,
  Palette,
  Lock,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

const ROLE_LABELS: Record<string, string> = {
  system_admin: 'System Administrator',
  corporate_manager: 'Corporate Manager',
  mine_manager: 'Mine Manager',
  mine_officer: 'Mine Officer',
  field_inspector: 'Field Inspector',
  regional_manager: 'Regional Manager',
  regulatory_auditor: 'Regulatory Auditor',
};
const formatRole = (role: string) => ROLE_LABELS[role] ?? role;

function applyTheme(theme: string) {
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else if (theme === 'light') {
    root.classList.remove('dark');
  } else {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }
}

const TIMEZONES = [
  { value: 'Asia/Kolkata', label: 'Asia/Kolkata (IST, UTC+5:30)' },
  { value: 'UTC', label: 'UTC (UTC+0)' },
  { value: 'America/New_York', label: 'America/New_York (EST/EDT)' },
  { value: 'America/Chicago', label: 'America/Chicago (CST/CDT)' },
  { value: 'America/Los_Angeles', label: 'America/Los_Angeles (PST/PDT)' },
  { value: 'Europe/London', label: 'Europe/London (GMT/BST)' },
  { value: 'Europe/Berlin', label: 'Europe/Berlin (CET/CEST)' },
  { value: 'Asia/Dubai', label: 'Asia/Dubai (GST, UTC+4)' },
  { value: 'Asia/Singapore', label: 'Asia/Singapore (SGT, UTC+8)' },
  { value: 'Asia/Tokyo', label: 'Asia/Tokyo (JST, UTC+9)' },
  { value: 'Australia/Sydney', label: 'Australia/Sydney (AEST/AEDT)' },
];

const NOTIFICATION_FIELDS = [
  { key: 'safety_alerts', label: 'Critical Safety Alerts', description: 'Receive alerts for high-risk safety events.' },
  { key: 'critical_risk_alerts', label: 'Critical Risk Alerts', description: 'Receive alerts when risk scores exceed critical thresholds.' },
  { key: 'compliance_alerts', label: 'Compliance Alerts', description: 'Receive notifications about compliance violations and issues.' },
  { key: 'overdue_action_reminders', label: 'Overdue Action Reminders', description: 'Receive reminders when corrective actions become overdue.' },
  { key: 'regulatory_updates', label: 'Regulatory Updates', description: 'Receive notifications about relevant regulatory changes.' },
  { key: 'inspection_reminders', label: 'Inspection Reminders', description: 'Receive reminders for upcoming or overdue inspections.' },
  { key: 'email_notifications', label: 'Email Notifications', description: 'Allow supported notifications to be delivered by email.' },
  { key: 'in_app_notifications', label: 'In-App Notifications', description: 'Enable notifications inside the governance platform.' },
] as const;
type NotifKey = (typeof NOTIFICATION_FIELDS)[number]['key'];

const TABS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'security', label: 'Security', icon: Lock },
  { id: 'appearance', label: 'Appearance', icon: Palette },
  { id: 'notifications', label: 'Notifications', icon: Bell },
] as const;
type TabId = (typeof TABS)[number]['id'];

function SectionHeader({ title, description }: { title: string; description: string }) {
  return (
    <div className="pb-3 border-b border-graphite-200">
      <h3 className="text-lg font-semibold text-graphite-900">{title}</h3>
      <p className="text-sm text-graphite-500 mt-0.5">{description}</p>
    </div>
  );
}

export default function Settings() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabId>('profile');
  const [fullName, setFullName] = useState('');
  const [pwForm, setPwForm] = useState({ current: '', next: '', confirm: '' });
  const [pwError, setPwError] = useState('');
  const [prefs, setPrefs] = useState({ theme: 'system', language: 'en', timezone: 'Asia/Kolkata' });
  const [notifs, setNotifs] = useState<Record<NotifKey, boolean>>({
    safety_alerts: true, critical_risk_alerts: true, compliance_alerts: true,
    overdue_action_reminders: true, regulatory_updates: true, inspection_reminders: true,
    email_notifications: true, in_app_notifications: true,
  });

  const { data: meData, isLoading: meLoading, isError: meError } = useQuery({
    queryKey: ['auth-me'],
    queryFn: () => apiClient.get('/api/v1/auth/me').then((r) => r.data),
    staleTime: 5 * 60 * 1000,
    enabled: !!user,
  });

  useEffect(() => {
    if (meData?.full_name) setFullName(meData.full_name);
  }, [meData]);

  const { isLoading: prefsLoading, isError: prefsError, refetch: refetchPrefs } = useQuery({
    queryKey: ['settings-prefs'],
    queryFn: async () => {
      const res = await apiClient.get('/api/v1/settings/preferences');
      setPrefs(res.data);
      applyTheme(res.data.theme ?? 'system');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const { isLoading: notifsLoading, isError: notifsError, refetch: refetchNotifs } = useQuery({
    queryKey: ['settings-notifs'],
    queryFn: async () => {
      const res = await apiClient.get('/api/v1/settings/notifications');
      setNotifs(res.data);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const updateProfileMut = useMutation({
    mutationFn: () => apiClient.patch('/api/v1/auth/me', { full_name: fullName.trim() }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['auth-me'] }); toast.success('Profile updated.'); },
    onError: (err: any) => { toast.error(err.response?.data?.detail ?? 'Failed to update profile.'); },
  });

  const changePasswordMut = useMutation({
    mutationFn: () => apiClient.post('/api/v1/auth/change-password', {
      current_password: pwForm.current,
      new_password: pwForm.next,
    }),
    onSuccess: () => { toast.success('Password changed.'); setPwForm({ current: '', next: '', confirm: '' }); setPwError(''); },
    onError: (err: any) => { toast.error(err.response?.data?.detail ?? 'Failed to change password.'); },
  });

  const savePrefsMut = useMutation({
    mutationFn: () => apiClient.put('/api/v1/settings/preferences', prefs),
    onSuccess: () => { applyTheme(prefs.theme); toast.success('Preferences saved.'); },
    onError: (err: any) => { toast.error(err.response?.data?.detail ?? 'Failed to save preferences.'); },
  });

  const saveNotifsMut = useMutation({
    mutationFn: () => apiClient.put('/api/v1/settings/notifications', notifs),
    onSuccess: () => { toast.success('Notification settings saved.'); },
    onError: (err: any) => { toast.error(err.response?.data?.detail ?? 'Failed to save notifications.'); },
  });

  const handlePasswordChange = () => {
    setPwError('');
    if (!pwForm.current || !pwForm.next || !pwForm.confirm) { setPwError('All fields are required.'); return; }
    if (pwForm.next !== pwForm.confirm) { setPwError('New password and confirmation do not match.'); return; }
    if (pwForm.next.length < 8) { setPwError('New password must be at least 8 characters.'); return; }
    changePasswordMut.mutate();
  };

  const isInitialLoading = meLoading || prefsLoading || notifsLoading;

  const initials = meData?.full_name
    ? meData.full_name.split(' ').map((p: string) => p[0]).join('').slice(0, 2).toUpperCase()
    : (user?.email?.[0] ?? 'U').toUpperCase();

  return (
    <div className="flex h-full flex-col lg:flex-row gap-4 lg:gap-6 p-4 lg:p-0 max-w-5xl mx-auto">
      <nav className="w-full lg:w-52 shrink-0 flex flex-row lg:flex-col gap-1 overflow-x-auto lg:overflow-visible">
        <h2 className="hidden lg:block text-xl font-bold text-graphite-900 mb-3 px-1">Settings</h2>
        {TABS.map(({ id, label, icon: Icon }) => {
          const active = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              aria-current={active ? 'page' : undefined}
              className={[
                'relative flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors whitespace-nowrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-mining-amber-500',
                active ? 'bg-graphite-900 text-white' : 'text-graphite-600 hover:bg-graphite-100 hover:text-graphite-900',
              ].join(' ')}
            >
              {active && <span className="absolute left-0 top-1/2 -mt-3 h-6 w-1 rounded-r bg-mining-amber-500 hidden lg:block" aria-hidden="true" />}
              <Icon size={15} className={active ? 'text-mining-amber-400' : 'text-graphite-400'} />
              {label}
            </button>
          );
        })}
      </nav>

      <div className="flex-1 min-w-0 bg-white rounded-xl border border-graphite-200 shadow-card p-6 lg:p-8">
        {isInitialLoading ? (
          <div className="space-y-6 max-w-2xl">
            <Skeleton className="h-7 w-48" />
            <Skeleton className="h-4 w-72" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : (
          <div className="max-w-2xl space-y-7">

            {activeTab === 'profile' && (
              <>
                <SectionHeader title="Profile Information" description="Your personal information and account details." />
                {meError && (
                  <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700" role="alert">
                    <AlertCircle size={15} aria-hidden="true" />
                    Could not load profile from server. Showing session data.
                  </div>
                )}
                <div className="flex items-center gap-4">
                  <div className="h-14 w-14 rounded-full bg-mining-amber-100 flex items-center justify-center text-mining-amber-800 font-bold text-lg shrink-0" aria-hidden="true">
                    {initials}
                  </div>
                  <div>
                    <p className="font-semibold text-graphite-900">{meData?.full_name ?? user?.email}</p>
                    <p className="text-sm text-graphite-500">{formatRole(meData?.role ?? user?.role ?? '')}</p>
                  </div>
                </div>
                <div className="grid gap-4">
                  <div className="grid gap-1.5">
                    <label htmlFor="full-name" className="text-sm font-medium text-graphite-700">Full Name</label>
                    <Input id="full-name" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Enter your full name" />
                  </div>
                  <div className="grid gap-1.5">
                    <label htmlFor="email" className="text-sm font-medium text-graphite-700">Email Address</label>
                    <Input id="email" value={meData?.email ?? user?.email ?? ''} disabled className="bg-graphite-50 text-graphite-500 cursor-not-allowed" />
                    <p className="text-xs text-graphite-400">Email cannot be changed here.</p>
                  </div>
                  <div className="grid gap-1.5">
                    <label htmlFor="role" className="text-sm font-medium text-graphite-700">Role</label>
                    <Input id="role" value={formatRole(meData?.role ?? user?.role ?? '')} disabled className="bg-graphite-50 text-graphite-500 cursor-not-allowed" />
                    <p className="text-xs text-graphite-400">Role is managed by your administrator.</p>
                  </div>
                </div>
                <Button onClick={() => updateProfileMut.mutate()} disabled={updateProfileMut.isPending || !fullName.trim()} className="bg-graphite-900 hover:bg-graphite-800 text-white">
                  {updateProfileMut.isPending ? <><Loader2 size={14} className="mr-2 animate-spin" />Saving&hellip;</> : 'Save Profile'}
                </Button>
              </>
            )}

            {activeTab === 'security' && (
              <>
                <SectionHeader title="Change Password" description="Keep your account secure by using a strong, unique password." />
                <div className="grid gap-4">
                  <div className="grid gap-1.5">
                    <label htmlFor="current-pw" className="text-sm font-medium text-graphite-700">Current Password</label>
                    <Input id="current-pw" type="password" value={pwForm.current} onChange={(e) => setPwForm({ ...pwForm, current: e.target.value })} placeholder="Enter current password" autoComplete="current-password" />
                  </div>
                  <div className="grid gap-1.5">
                    <label htmlFor="new-pw" className="text-sm font-medium text-graphite-700">New Password</label>
                    <Input id="new-pw" type="password" value={pwForm.next} onChange={(e) => setPwForm({ ...pwForm, next: e.target.value })} placeholder="At least 8 characters" autoComplete="new-password" />
                  </div>
                  <div className="grid gap-1.5">
                    <label htmlFor="confirm-pw" className="text-sm font-medium text-graphite-700">Confirm New Password</label>
                    <Input id="confirm-pw" type="password" value={pwForm.confirm} onChange={(e) => setPwForm({ ...pwForm, confirm: e.target.value })} placeholder="Repeat new password" autoComplete="new-password" />
                  </div>
                  {pwError && (
                    <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700" role="alert">
                      <AlertCircle size={14} aria-hidden="true" />{pwError}
                    </div>
                  )}
                </div>
                <Button onClick={handlePasswordChange} disabled={changePasswordMut.isPending} className="bg-graphite-900 hover:bg-graphite-800 text-white">
                  {changePasswordMut.isPending ? <><Loader2 size={14} className="mr-2 animate-spin" />Changing&hellip;</> : 'Change Password'}
                </Button>
              </>
            )}

            {activeTab === 'appearance' && (
              <>
                <SectionHeader title="Appearance Preferences" description="Customize how the application looks and behaves." />
                {prefsError && (
                  <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700" role="alert">
                    <AlertCircle size={15} aria-hidden="true" />
                    Could not load preferences.{' '}
                    <button onClick={() => refetchPrefs()} className="underline font-medium hover:text-red-900">Retry</button>
                  </div>
                )}
                <div className="grid gap-6">
                  <div className="grid gap-1.5">
                    <label htmlFor="theme-select" className="text-sm font-medium text-graphite-700">Theme</label>
                    <Select value={prefs.theme} onValueChange={(v) => { setPrefs({ ...prefs, theme: v }); applyTheme(v); }}>
                      <SelectTrigger id="theme-select"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">Light</SelectItem>
                        <SelectItem value="dark">Dark</SelectItem>
                        <SelectItem value="system">System Default</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-graphite-400">"System Default" follows your OS dark/light preference.</p>
                  </div>
                  <div className="grid gap-1.5">
                    <label htmlFor="lang-select" className="text-sm font-medium text-graphite-700">Language</label>
                    <Select value={prefs.language} onValueChange={(v) => setPrefs({ ...prefs, language: v })}>
                      <SelectTrigger id="lang-select"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English (US)</SelectItem>
                        <SelectItem value="hi">Hindi (translations in development)</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-graphite-400">English is the current fully supported interface language.</p>
                  </div>
                  <div className="grid gap-1.5">
                    <label htmlFor="tz-select" className="text-sm font-medium text-graphite-700">Timezone</label>
                    <Select value={prefs.timezone} onValueChange={(v) => setPrefs({ ...prefs, timezone: v })}>
                      <SelectTrigger id="tz-select"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {TIMEZONES.map((tz) => (
                          <SelectItem key={tz.value} value={tz.value}>{tz.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-graphite-400">Used to display deadlines and timestamps in your local time.</p>
                  </div>
                </div>
                <Button onClick={() => savePrefsMut.mutate()} disabled={savePrefsMut.isPending} className="bg-graphite-900 hover:bg-graphite-800 text-white">
                  {savePrefsMut.isPending ? <><Loader2 size={14} className="mr-2 animate-spin" />Saving&hellip;</> : 'Save Preferences'}
                </Button>
                <div className="rounded-lg bg-graphite-50 border border-graphite-200 px-4 py-3 text-xs text-graphite-500">
                  <strong>Note:</strong> Default Mine selector is deferred — a role-scoped mine picker will be added in a future release.
                </div>
              </>
            )}

            {activeTab === 'notifications' && (
              <>
                <SectionHeader title="Notification Settings" description="Manage which alerts and reminders you receive." />
                {notifsError && (
                  <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700" role="alert">
                    <AlertCircle size={15} aria-hidden="true" />
                    Could not load notification settings.{' '}
                    <button onClick={() => refetchNotifs()} className="underline font-medium hover:text-red-900">Retry</button>
                  </div>
                )}
                <div className="divide-y divide-graphite-100">
                  {NOTIFICATION_FIELDS.map(({ key, label, description }) => (
                    <div key={key} className="flex items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
                      <div className="flex-1 min-w-0">
                        <label htmlFor={`notif-${key}`} className="text-sm font-medium text-graphite-900 cursor-pointer">{label}</label>
                        <p className="text-xs text-graphite-500 mt-0.5">{description}</p>
                      </div>
                      <Switch
                        id={`notif-${key}`}
                        checked={notifs[key]}
                        onCheckedChange={(checked) => setNotifs((prev) => ({ ...prev, [key]: checked }))}
                      />
                    </div>
                  ))}
                </div>
                <Button onClick={() => saveNotifsMut.mutate()} disabled={saveNotifsMut.isPending} className="bg-graphite-900 hover:bg-graphite-800 text-white">
                  {saveNotifsMut.isPending ? <><Loader2 size={14} className="mr-2 animate-spin" />Saving&hellip;</> : 'Save Notifications'}
                </Button>
              </>
            )}

          </div>
        )}
      </div>
    </div>
  );
}