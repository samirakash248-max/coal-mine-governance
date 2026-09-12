import { useState } from 'react';
import { useAuth } from '../providers/AuthProvider';
import { apiClient } from '../api/client';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Skeleton } from '../components/ui/skeleton';
import { User, Bell, Palette } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

export default function Settings() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  
  const [prefs, setPrefs] = useState({ theme: 'system', language: 'en', timezone: 'UTC' });
  const [notifs, setNotifs] = useState({
    inspection_reminders: true,
    safety_alerts: true,
    email_notifications: true
  });

  const { isLoading: loading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const [prefsRes, notifsRes] = await Promise.all([
        apiClient.get('/settings/preferences'),
        apiClient.get('/settings/notifications')
      ]);
      if (prefsRes.data) setPrefs(prefsRes.data);
      if (notifsRes.data) setNotifs(notifsRes.data);
      return true;
    },
    staleTime: 5 * 60 * 1000,
  });

  const savePreferences = async () => {
    await apiClient.put('/settings/preferences', prefs);
    alert('Preferences saved!');
  };

  const saveNotifications = async () => {
    await apiClient.put('/settings/notifications', notifs);
    alert('Notifications saved!');
  };

  return (
    <div className="flex h-full flex-col md:flex-row gap-6 p-6 max-w-7xl mx-auto">
      <div className="w-full md:w-64 space-y-2 shrink-0">
        <h2 className="text-2xl font-bold mb-6 text-gray-900">Settings</h2>
        
        <button 
          onClick={() => setActiveTab('profile')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left text-sm font-medium transition-colors ${activeTab === 'profile' ? 'bg-primary text-white' : 'text-gray-700 hover:bg-gray-100'}`}
        >
          <User className="w-5 h-5" /> Profile
        </button>
        
        <button 
          onClick={() => setActiveTab('appearance')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left text-sm font-medium transition-colors ${activeTab === 'appearance' ? 'bg-primary text-white' : 'text-gray-700 hover:bg-gray-100'}`}
        >
          <Palette className="w-5 h-5" /> Appearance
        </button>
        
        <button 
          onClick={() => setActiveTab('notifications')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left text-sm font-medium transition-colors ${activeTab === 'notifications' ? 'bg-primary text-white' : 'text-gray-700 hover:bg-gray-100'}`}
        >
          <Bell className="w-5 h-5" /> Notifications
        </button>
      </div>
      
      <div className="flex-1 bg-white p-8 rounded-xl border shadow-sm">
        {loading ? (
          <div className="space-y-6 max-w-2xl">
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-64 mb-6" />
            
            <div className="grid gap-4">
              <div className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-10 w-full" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-10 w-full" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-10 w-full" />
              </div>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'profile' && (
              <div className="space-y-6 max-w-2xl">
                <div>
                  <h3 className="text-xl font-bold">Profile Information</h3>
                  <p className="text-gray-500 text-sm">Your personal information and role details.</p>
                </div>
                
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-gray-700">Full Name</label>
                    <Input value={(user as any)?.full_name || ''} disabled />
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-gray-700">Email Address</label>
                    <Input value={user?.email || ''} disabled />
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-gray-700">Role</label>
                    <Input value={user?.role || ''} disabled className="uppercase" />
                  </div>
                </div>
              </div>
            )}
            
            {activeTab === 'appearance' && (
              <div className="space-y-6 max-w-2xl">
                <div>
                  <h3 className="text-xl font-bold">Appearance Preferences</h3>
                  <p className="text-gray-500 text-sm">Customize how the application looks to you.</p>
                </div>
                
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-gray-700">Theme</label>
                    <select 
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      value={prefs.theme}
                      onChange={(e) => setPrefs({...prefs, theme: e.target.value})}
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="system">System Default</option>
                    </select>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-gray-700">Language</label>
                    <select 
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      value={prefs.language}
                      onChange={(e) => setPrefs({...prefs, language: e.target.value})}
                    >
                      <option value="en">English (US)</option>
                      <option value="hi">Hindi</option>
                    </select>
                  </div>
                  <Button onClick={savePreferences} className="mt-4 w-32">Save Changes</Button>
                </div>
              </div>
            )}
            
            {activeTab === 'notifications' && (
              <div className="space-y-6 max-w-2xl">
                <div>
                  <h3 className="text-xl font-bold">Notification Settings</h3>
                  <p className="text-gray-500 text-sm">Manage when and how you receive alerts.</p>
                </div>
                
                <div className="space-y-4">
                  <label className="flex items-center gap-3">
                    <input type="checkbox" checked={notifs.safety_alerts} onChange={(e) => setNotifs({...notifs, safety_alerts: e.target.checked})} className="w-4 h-4 text-primary" />
                    <span className="text-sm font-medium">Critical Safety Alerts</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input type="checkbox" checked={notifs.inspection_reminders} onChange={(e) => setNotifs({...notifs, inspection_reminders: e.target.checked})} className="w-4 h-4 text-primary" />
                    <span className="text-sm font-medium">Inspection Reminders</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input type="checkbox" checked={notifs.email_notifications} onChange={(e) => setNotifs({...notifs, email_notifications: e.target.checked})} className="w-4 h-4 text-primary" />
                    <span className="text-sm font-medium">Email Notifications</span>
                  </label>
                  
                  <Button onClick={saveNotifications} className="mt-6 w-32">Save Changes</Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
