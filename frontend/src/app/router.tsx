import { createBrowserRouter } from 'react-router-dom';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { OverviewPage } from '../pages/OverviewPage';
import { ForecastPage } from '../pages/ForecastPage';
import { AccuracyPage } from '../pages/AccuracyPage';
import { MethodologyPage } from '../pages/MethodologyPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <DashboardLayout />,
    children: [
      {
        index: true,
        element: <OverviewPage />,
      },
      {
        path: 'forecasts',
        element: <ForecastPage />,
      },
      {
        path: 'accuracy',
        element: <AccuracyPage />,
      },
      {
        path: 'methodology',
        element: <MethodologyPage />,
      },
      {
        path: '*',
        element: <OverviewPage />,
      },
    ],
  },
]);
