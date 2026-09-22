import { useState, useEffect } from "react";
import { Shield, CheckCircle2, XCircle, MoreHorizontal, UserX, Loader2 } from "lucide-react";
import { apiClient } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner"; // Assuming sonner is used based on UI folder

export type Role = "SYSTEM_ADMIN" | "CORPORATE_MANAGER" | "MINE_MANAGER" | "MINE_OFFICER" | "FIELD_INSPECTOR" | "REGULATORY_AUDITOR";

export interface UserData {
  id: string;
  full_name: string;
  email: string;
  role: Role;
  is_active: boolean;
  mine_id: string | null;
}

export function TeamAccessManager() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      // Using generic users endpoint; in production you might filter by mine_id if required.
      const res = await apiClient.get<UserData[]>("/users");
      setUsers(res.data);
    } catch (error) {
      toast.error("Failed to fetch team members");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: Role) => {
    try {
      setProcessingId(userId);
      await apiClient.patch(`/users/${userId}`, { role: newRole });
      
      setUsers((prev) => 
        prev.map((user) => user.id === userId ? { ...user, role: newRole } : user)
      );
      toast.success("Role updated successfully");
    } catch (error) {
      toast.error("Failed to update user role");
      console.error(error);
    } finally {
      setProcessingId(null);
    }
  };

  const handleToggleAccess = async (userId: string, currentStatus: boolean) => {
    try {
      setProcessingId(userId);
      await apiClient.patch(`/users/${userId}`, { is_active: !currentStatus });
      
      setUsers((prev) => 
        prev.map((user) => user.id === userId ? { ...user, is_active: !currentStatus } : user)
      );
      toast.success(`User access ${!currentStatus ? 'restored' : 'revoked'}`);
    } catch (error) {
      toast.error("Failed to modify user access");
      console.error(error);
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 border rounded-md">
        <Loader2 className="w-8 h-8 animate-spin text-gray-500" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Shield className="w-5 h-5 text-mining-amber-600" />
            Team Access Management
          </h2>
          <p className="text-sm text-gray-500">Manage personnel roles and system access limits.</p>
        </div>
      </div>

      <div className="border rounded-md bg-white overflow-hidden shadow-sm">
        <Table>
          <TableHeader className="bg-gray-50">
            <TableRow>
              <TableHead>Personnel</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="h-24 text-center text-gray-500">
                  No personnel records found.
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow key={user.id} className={!user.is_active ? "opacity-60 bg-gray-50" : ""}>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium text-gray-900">{user.full_name}</span>
                      <span className="text-xs text-gray-500">{user.email}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Select 
                      disabled={processingId === user.id || !user.is_active}
                      value={user.role} 
                      onValueChange={(val) => handleRoleChange(user.id, val as Role)}
                    >
                      <SelectTrigger className="w-[200px] h-8 text-xs">
                        <SelectValue placeholder="Select role" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="SYSTEM_ADMIN">System Admin</SelectItem>
                        <SelectItem value="CORPORATE_MANAGER">Corporate Manager</SelectItem>
                        <SelectItem value="MINE_MANAGER">Mine Manager</SelectItem>
                        <SelectItem value="MINE_OFFICER">Mine Officer</SelectItem>
                        <SelectItem value="FIELD_INSPECTOR">Field Inspector</SelectItem>
                        <SelectItem value="REGULATORY_AUDITOR">DGMS Regulator</SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell>
                    {user.is_active ? (
                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Active
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 gap-1">
                        <XCircle className="w-3 h-3" /> Revoked
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0" disabled={processingId === user.id}>
                          <span className="sr-only">Open menu</span>
                          {processingId === user.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <MoreHorizontal className="h-4 w-4" />
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Account Actions</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => handleToggleAccess(user.id, user.is_active)}
                          className={user.is_active ? "text-red-600 focus:bg-red-50 focus:text-red-700" : "text-green-600 focus:bg-green-50"}
                        >
                          {user.is_active ? (
                            <><UserX className="mr-2 h-4 w-4" /> Revoke Access</>
                          ) : (
                            <><CheckCircle2 className="mr-2 h-4 w-4" /> Restore Access</>
                          )}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
