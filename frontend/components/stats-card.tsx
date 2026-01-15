import { cn } from "@/lib/utils";
import { Card, CardContent } from "./ui/card";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: "up" | "down" | "neutral";
}

export function StatsCard({ title, value, subtitle, icon: Icon, trend }: StatsCardProps) {
  return (
    <Card className="bg-card/50 backdrop-blur">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className={cn(
              "text-2xl font-bold mt-1",
              trend === "up" && "text-bullish",
              trend === "down" && "text-bearish"
            )}>
              {value}
            </p>
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
            )}
          </div>
          <div className={cn(
            "p-2 rounded-lg",
            trend === "up" && "bg-bullish/10 text-bullish",
            trend === "down" && "bg-bearish/10 text-bearish",
            !trend && "bg-muted text-muted-foreground"
          )}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
