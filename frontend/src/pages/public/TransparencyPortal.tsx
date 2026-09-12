import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Mountain, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function TransparencyPortal() {
  return (
    <div className="space-y-8">
      <div className="text-center space-y-4 py-8">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">Public Transparency Portal</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          We are committed to maintaining the highest safety and compliance standards. 
          Here you can view aggregated, high-level statistics about our operations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-t-4 border-t-green-500 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Overall Compliance</CardTitle>
            <ShieldCheck className="h-5 w-5 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">92.4%</div>
            <p className="text-xs text-gray-500 mt-1">Across all active regions</p>
          </CardContent>
        </Card>

        <Card className="border-t-4 border-t-primary-500 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Total Active Mines</CardTitle>
            <Mountain className="h-5 w-5 text-primary-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">14</div>
            <p className="text-xs text-gray-500 mt-1">Currently in operation</p>
          </CardContent>
        </Card>

        <Card className="border-t-4 border-t-amber-500 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Safety Observations</CardTitle>
            <AlertTriangle className="h-5 w-5 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">128</div>
            <p className="text-xs text-gray-500 mt-1">Reported this month</p>
          </CardContent>
        </Card>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mt-12">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">Our Commitment</h2>
        <p className="text-gray-600 mb-4">
          Safety and environmental stewardship are at the core of our operations. We continuously monitor and evaluate our sites to ensure compliance with all national and international regulations.
        </p>
        <p className="text-gray-600">
          * Note: Due to privacy and security reasons, personally identifiable information (PII) and specific mine locations are abstracted in this public portal.
        </p>
      </div>
    </div>
  );
}
