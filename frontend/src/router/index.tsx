import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppShell } from '../layouts/AppShell';
import { PublicLayout } from '../layouts/PublicLayout';
import { ProtectedRoute } from './ProtectedRoute';
import Login from '../pages/Login';
import Unauthorized from '../pages/Unauthorized';
import Dashboard from '../pages/Dashboard';
import DailyBrief from '../pages/DailyBrief';
import MineList from '../pages/mines/MineList';
import MineDetail from '../pages/mines/MineDetail';
import Calendar from '../pages/compliance/Calendar';
import ReportEvent from '../pages/field/ReportEvent';
import CorrectiveActions from '../pages/field/CorrectiveActions';
import { GovernanceMap } from '../pages/gis/GovernanceMap';
import DocumentLibrary from '../pages/documents/DocumentLibrary';
import VerifyDocument from '../pages/documents/VerifyDocument';
import GrievancesList from '../pages/grievances/GrievancesList';
import ExecutiveDashboard from '../pages/analytics/ExecutiveDashboard';
import ReportsManager from '../pages/reports/ReportsManager';
import TransparencyPortal from '../pages/public/TransparencyPortal';
import Settings from '../pages/Settings';
import Inspections from '../pages/Inspections';
import CreateInspection from '../pages/inspections/CreateInspection';
import InspectionDetail from '../pages/inspections/InspectionDetail';
import Safety from '../pages/Safety';
import ReportNearMiss from '../pages/safety/ReportNearMiss';
import EventDetail from '../pages/safety/EventDetail';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/unauthorized',
    element: <Unauthorized />,
  },
  {
    path: '/public',
    element: <PublicLayout />,
    children: [
      {
        index: true,
        element: <TransparencyPortal />,
      }
    ]
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'daily-brief',
        element: <DailyBrief />,
      },
      {
        path: 'gis',
        element: <GovernanceMap />,
      },
      {
        path: 'mines',
        element: <MineList />,
      },
      {
        path: 'mines/:id',
        element: <MineDetail />,
      },
      {
        path: 'compliance/calendar',
        element: <Calendar />,
      },
      {
        path: 'field/report',
        element: <ReportEvent />,
      },
      {
        path: 'field/actions',
        element: <CorrectiveActions />,
      },
      {
        path: 'documents',
        element: <DocumentLibrary />,
      },
      {
        path: 'documents/:id/verify',
        element: <VerifyDocument />,
      },
      {
        path: 'grievances',
        element: <GrievancesList />,
      },
      {
        path: 'analytics',
        element: <ExecutiveDashboard />,
      },
      {
        path: 'reports',
        element: <ReportsManager />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: 'inspections',
        element: <Inspections />,
      },
      {
        path: 'inspections/new',
        element: <CreateInspection />,
      },
      {
        path: 'inspections/:id',
        element: <InspectionDetail />,
      },
      {
        path: 'safety',
        element: <Safety />,
      },
      {
        path: 'safety/report-near-miss',
        element: <ReportNearMiss />,
      },
      {
        path: 'safety/:id',
        element: <EventDetail />,
      },
    ],
  },
]);
