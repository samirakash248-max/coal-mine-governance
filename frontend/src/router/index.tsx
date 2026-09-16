import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppShell } from '../layouts/AppShell';
import { PublicLayout } from '../layouts/PublicLayout';
import { ProtectedRoute } from './ProtectedRoute';
import Login from '../pages/Login';
import AuthCallback from '../pages/AuthCallback';
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
import RiskIntelligence from '../pages/risk/RiskIntelligence';
import AuditTrail from '../pages/audit/AuditTrail';
import EnvironmentalIntelligence from '../pages/weather/EnvironmentalIntelligence';
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
    path: '/auth/callback',
    element: <AuthCallback />,
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
        element: <ProtectedRoute requiredPermission="dashboard:read"><Dashboard /></ProtectedRoute>,
      },
      {
        path: 'daily-brief',
        element: <ProtectedRoute requiredPermission="dashboard:read"><DailyBrief /></ProtectedRoute>,
      },
      {
        path: 'gis',
        element: <ProtectedRoute requiredPermission="mine:read"><GovernanceMap /></ProtectedRoute>,
      },
      {
        path: 'mines',
        element: <ProtectedRoute requiredPermission="mine:read"><MineList /></ProtectedRoute>,
      },
      {
        path: 'mines/:id',
        element: <ProtectedRoute requiredPermission="mine:read"><MineDetail /></ProtectedRoute>,
      },
      {
        path: 'compliance/calendar',
        element: <ProtectedRoute requiredPermission="compliance:read"><Calendar /></ProtectedRoute>,
      },
      {
        path: 'field/report',
        element: <ProtectedRoute requiredPermission="safety:create"><ReportEvent /></ProtectedRoute>,
      },
      {
        path: 'field/actions',
        element: <ProtectedRoute requiredPermission="safety:read"><CorrectiveActions /></ProtectedRoute>,
      },
      {
        path: 'documents',
        element: <ProtectedRoute requiredPermission="document:read"><DocumentLibrary /></ProtectedRoute>,
      },
      {
        path: 'documents/:id/verify',
        element: <ProtectedRoute requiredPermission="document:verify"><VerifyDocument /></ProtectedRoute>,
      },
      {
        path: 'grievances',
        element: <ProtectedRoute requiredPermission="grievance:read"><GrievancesList /></ProtectedRoute>,
      },
      {
        path: 'analytics',
        element: <ProtectedRoute requiredPermission="report:read"><ExecutiveDashboard /></ProtectedRoute>,
      },
      {
        path: 'reports',
        element: <ProtectedRoute requiredPermission="report:read"><ReportsManager /></ProtectedRoute>,
      },
      {
        path: 'risk',
        element: <ProtectedRoute requiredPermission="risk:read"><RiskIntelligence /></ProtectedRoute>,
      },
      {
        path: 'audit',
        element: <ProtectedRoute requiredPermission="audit:read"><AuditTrail /></ProtectedRoute>,
      },
      {
        path: 'weather',
        element: <ProtectedRoute requiredPermission="weather:read"><EnvironmentalIntelligence /></ProtectedRoute>,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: 'inspections',
        element: <ProtectedRoute requiredPermission="inspection:read"><Inspections /></ProtectedRoute>,
      },
      {
        path: 'inspections/new',
        element: <ProtectedRoute requiredPermission="inspection:create"><CreateInspection /></ProtectedRoute>,
      },
      {
        path: 'inspections/:id',
        element: <ProtectedRoute requiredPermission="inspection:read"><InspectionDetail /></ProtectedRoute>,
      },
      {
        path: 'safety',
        element: <ProtectedRoute requiredPermission="safety:read"><Safety /></ProtectedRoute>,
      },
      {
        path: 'safety/report-near-miss',
        element: <ProtectedRoute requiredPermission="safety:create"><ReportNearMiss /></ProtectedRoute>,
      },
      {
        path: 'safety/:id',
        element: <ProtectedRoute requiredPermission="safety:read"><EventDetail /></ProtectedRoute>,
      },
    ],
  },
]);



