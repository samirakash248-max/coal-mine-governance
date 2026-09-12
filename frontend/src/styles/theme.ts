export const colors = {
  graphite: {
    50: '#f7f7f8', 100: '#eeeef0', 200: '#d9d9de', 300: '#b8b8c1',
    400: '#91919f', 500: '#737384', 600: '#5d5d6c', 700: '#4c4c58',
    800: '#41414b', 900: '#393941', 950: '#1a1a1f',
  },
  earth: {
    50: '#faf8f5', 100: '#f3efe8', 200: '#e6ddd0', 300: '#d5c5b0',
    400: '#c2a88e', 500: '#b39275', 600: '#a67f65', 700: '#8b6854',
    800: '#725648', 900: '#5e483d', 950: '#322420',
  },
  miningAmber: {
    50: '#fefce8', 100: '#fef9c3', 200: '#fef08a', 300: '#fde047',
    400: '#facc15', 500: '#eab308', 600: '#ca8a04', 700: '#a16207',
    800: '#854d0e', 900: '#713f12', 950: '#422006',
  },
  status: {
    healthy: '#16a34a',
    warning: '#d97706',
    elevated: '#ea580c',
    critical: '#dc2626',
    info: '#2563eb',
    inactive: '#6b7280',
  },
} as const;

export const chartColors = [
  colors.miningAmber[500],
  colors.graphite[600],
  colors.status.info,
  colors.status.healthy,
  colors.earth[500],
  colors.status.elevated,
] as const;
