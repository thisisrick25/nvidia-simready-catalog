"use client";

import { useMemo, useState } from "react";
import {
  Activity,
  Boxes,
  CircleHelp,
  Database,
  ExternalLink,
  LayoutDashboard,
  ShieldCheck,
  Search,
  X,
  ChevronDown,
  Eye,
} from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import assets from "../public/data/assets.json";
import stats from "../public/data/stats.json";
import validation from "../public/data/validation.json";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableCaption,
} from "@/components/ui/table";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui/tabs";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from "@/components/ui/tooltip";
import {
  ScrollArea,
} from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

interface Asset {
  asset: string;
  asset_type: string | null;
  taxonomy_root: string | null;
  taxonomy_group: string | null;
  uuid: string | null;
  up_axis: string | null;
  meters_per_unit: number | null;
  variants: string[];
  mesh_count: number | null;
  rigid_body_count: number | null;
  mass_kg: number | null;
  has_articulation: boolean | null;
  joint_types: string | null;
  materials: string | null;
  shader_classes: string | null;
  semantic_tokens: string | null;
  validation_profile: string | null;
  validation_profile_version: string | null;
  validated_date: string | null;
  export_profile: string | null;
  features_total: number | null;
  features_passed: number | null;
  all_features_passed: boolean | null;
  failing_features: string | null;
  license: string | null;
  package_id: string | null;
  packaged_date: string | null;
  asset_info_mass_kg: number | null;
  asset_info_category: string | null;
  size_total_bytes: number | null;
  size_payload_bytes: number | null;
  geometry_size_bytes: number | null;
  texture_size_bytes: number | null;
  source_asset_size_bytes: number | null;
  metadata_size_bytes: number | null;
  metadata_file_count: number | null;
  bom_file_count: number | null;
  bom_entry_count: number | null;
  bom_hash_count: number | null;
  package_hash_count: number | null;
  package_format_version: string | null;
  conformance_file_count: number | null;
  conformance_profile: string | null;
  conformance_versions: string | null;
  provenance_tool: string | null;
  provenance_generated_date: string | null;
  provenance_exported_date: string | null;
  thumb_url: string | null;
  parse_status: string | null;
  parse_error: string | null;
  usd_date_generated: string | null;
}

interface ValidationRow {
  asset: string;
  feature: string;
  version: string;
  passed: boolean;
  failing_requirements: string;
  dependencies: string;
  validated_date: string;
  profile: string;
}

const typedAssets = assets as Asset[];
const typedValidation = validation as ValidationRow[];

type View = "overview" | "assets" | "validation" | "about";

const NVIDIA_GREEN = "#76b900";
const CHART_COLORS = [NVIDIA_GREEN, "#2f70bb", "#a86f0c", "#bb3038", "#1e7b4f"];

const formatBytes = (value: number | null | undefined) =>
  value == null || value === 0 ? "—" : `${(value / 1e6).toFixed(1)} MB`;

const formatMass = (value: number | null | undefined) =>
  value == null ? "—" : `${value.toPrecision(3)} kg`;

const formatNumber = (value: number | null | undefined) =>
  value == null ? "—" : value.toLocaleString('en-US');

function KpiCard({ label, value, note, trend }: { label: string; value: string; note: string; trend?: string }) {
  return (
    <Card className="kpi-card">
      <CardContent className="pt-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</p>
            <p className="text-3xl font-semibold text-foreground tabular-nums">{value}</p>
            <p className="text-sm text-muted-foreground">{note}</p>
          </div>
          {trend && (
            <Badge variant="secondary" className="text-xs">
              {trend}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function SectionCard({ title, description, children, className }: { title: string; description?: string; children: React.ReactNode; className?: string }) {
  return (
    <Card className={cn("section-card", className)}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function MassHistogramChart() {
  const massData = useMemo(() => {
    const masses = typedAssets
      .map((a) => a.mass_kg)
      .filter((m): m is number => m != null && m > 0);
    if (masses.length === 0) return [];
    const min = Math.min(...masses);
    const max = Math.max(...masses);
    const binCount = 30;
    const bins = Array.from({ length: binCount }, (_, i) => {
      const logMin = Math.log10(min);
      const logMax = Math.log10(max * 1.01);
      const step = (logMax - logMin) / binCount;
      const start = Math.pow(10, logMin + i * step);
      const end = Math.pow(10, logMin + (i + 1) * step);
      return { start, end, count: 0 };
    });
    masses.forEach((m) => {
      const bin = bins.find((b) => m >= b.start && m < b.end) || bins[bins.length - 1];
      bin.count++;
    });
    return bins.map((b) => ({
      range: `${b.start.toPrecision(2)}–${b.end.toPrecision(2)}`,
      count: b.count,
      start: b.start,
    }));
  }, []);

  if (massData.length === 0) {
    return (
      <Card className="h-64 flex items-center justify-center">
        <p className="text-muted-foreground">No mass data available</p>
      </Card>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={massData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
        <XAxis type="number" dataKey="count" tick={{ fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="range"
          width={100}
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
        />
        <RechartsTooltip
          formatter={(value: any) =>
            value != null ? [value.toLocaleString(), "assets"] : ["—", "assets"]
          }
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e4e4e7",
            borderRadius: "6px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
          }}
        />
        <Bar
          dataKey="count"
          fill={NVIDIA_GREEN}
          radius={[0, 4, 4, 0]}
          maxBarSize={24}
        >
          {massData.map((_, index) => (
            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function SizeHistogramChart() {
  const sizeData = useMemo(() => {
    const sizes = typedAssets
      .map((a) => a.size_total_bytes)
      .filter((s): s is number => s != null && s > 0)
      .map((s) => s / 1e6);
    if (sizes.length === 0) return [];
    const min = Math.max(Math.min(...sizes), 0.001);
    const max = Math.max(...sizes);
    const binCount = 30;
    const bins = Array.from({ length: binCount }, (_, i) => {
      const logMin = Math.log10(min);
      const logMax = Math.log10(max * 1.01);
      const step = (logMax - logMin) / binCount;
      const start = Math.pow(10, logMin + i * step);
      const end = Math.pow(10, logMin + (i + 1) * step);
      return { start, end, count: 0 };
    });
    sizes.forEach((s) => {
      const bin = bins.find((b) => s >= b.start && s < b.end) || bins[bins.length - 1];
      bin.count++;
    });
    return bins.map((b) => ({
      range: `${b.start.toPrecision(2)}–${b.end.toPrecision(2)}`,
      count: b.count,
      start: b.start,
    }));
  }, []);

  if (sizeData.length === 0) {
    return (
      <Card className="h-64 flex items-center justify-center">
        <p className="text-muted-foreground">No size data available</p>
      </Card>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={sizeData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
        <XAxis type="number" dataKey="count" tick={{ fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="range"
          width={100}
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
        />
        <RechartsTooltip
          formatter={(value: any) =>
            value != null ? [value.toLocaleString(), "assets"] : ["—", "assets"]
          }
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e4e4e7",
            borderRadius: "6px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
          }}
        />
        <Bar
          dataKey="count"
          fill={NVIDIA_GREEN}
          radius={[0, 4, 4, 0]}
          maxBarSize={24}
        >
          {sizeData.map((_, index) => (
            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function VariantsChart() {
  const variantData = useMemo(() => {
    const vc = stats.variant_counts || {};
    return Object.entries(vc).map(([name, count]) => ({ name, count: count as number }));
  }, []);

  if (variantData.length === 0) {
    return (
      <Card className="h-64 flex items-center justify-center">
        <p className="text-muted-foreground">No variant data available</p>
      </Card>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={variantData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11 }} />
        <RechartsTooltip
          formatter={(value: any) =>
            value != null ? [value.toLocaleString(), "assets"] : ["—", "assets"]
          }
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e4e4e7",
            borderRadius: "6px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
          }}
        />
        <Bar dataKey="count" fill={NVIDIA_GREEN} radius={[4, 4, 0, 0]} maxBarSize={40}>
          {variantData.map((_, index) => (
            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function GrowthChart() {
  const growthData = useMemo(() => {
    const growth: Record<string, number> = stats.growth_by_date || {};
    const keys = Object.keys(growth).sort();
    let cumulative = 0;
    return keys.map((date) => {
      cumulative += growth[date];
      return { date, cumulative };
    });
  }, []);

  if (growthData.length === 0) {
    return (
      <Card className="h-64 flex items-center justify-center">
        <p className="text-muted-foreground">No growth data available</p>
      </Card>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={growthData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
        <YAxis tick={{ fontSize: 11 }} />
        <RechartsTooltip
          formatter={(value: any) =>
            value != null ? [value.toLocaleString(), "assets"] : ["—", "assets"]
          }
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e4e4e7",
            borderRadius: "6px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
          }}
        />
        <Line
          type="monotone"
          dataKey="cumulative"
          stroke={NVIDIA_GREEN}
          strokeWidth={2}
          dot={{ fill: NVIDIA_GREEN, strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6, fill: "#fff", stroke: NVIDIA_GREEN, strokeWidth: 2 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function ValidationPassRatesChart() {
  const rates = stats.validation_feature_rates || {};
  const chartData = useMemo(() =>
    Object.entries(rates)
      .map(([feature, [passed, total]]) => ({
        feature,
        passed: passed as number,
        total: total as number,
        rate: total > 0 ? (passed as number) / (total as number) * 100 : 0,
      }))
      .sort((a, b) => a.rate - b.rate),
    [rates]
  );

  if (chartData.length === 0) {
    return (
      <Card className="h-64 flex items-center justify-center">
        <p className="text-muted-foreground">No validation data available</p>
      </Card>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
        <YAxis
          type="category"
          dataKey="feature"
          width={180}
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
        />
        <RechartsTooltip
          formatter={(value: any, name: any) => [
            value != null ? value.toFixed(1) : "—",
            name === "rate" ? "% pass rate" : "assets",
          ]}
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e4e4e7",
            borderRadius: "6px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
          }}
        />
        <Bar
          dataKey="rate"
          fill={NVIDIA_GREEN}
          radius={[0, 4, 4, 0]}
          maxBarSize={20}
        >
          {chartData.map((_, index) => (
            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function Overview({ onNavigate }: { onNavigate: (view: View) => void }) {
  const massStats = stats.mass_stats || {};
  const failingReq = stats.failing_requirements_top?.[0] || ["—", 0];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Assets indexed"
          value={formatNumber(stats.n_assets)}
          note="complete catalog"
        />
        <KpiCard
          label="Dataset volume"
          value={`${stats.total_size_gb} GB`}
          note={`${formatNumber(stats.n_files)} files`}
        />
        <KpiCard
          label="Validation pass"
          value={`${stats.validation_pass_rate ?? "—"}%`}
          note="FET feature checks"
          trend="positive"
        />
        <KpiCard
          label="Articulated"
          value={formatNumber(stats.articulated_count)}
          note={`${stats.articulated_pct}% of assets`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Mass distribution" description="Log-scale view of per-asset physics mass">
          <MassHistogramChart />
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              Median: <strong className="text-foreground">{massStats.median?.toFixed(2) ?? "—"} kg</strong>
            </p>
          </div>
        </SectionCard>

        <SectionCard title="Download size" description="Log-scale view of asset download size">
          <SizeHistogramChart />
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              Median:{" "}
              <strong className="text-foreground">
                {stats.size_mb_stats?.median?.toFixed(2) ?? "—"} MB
              </strong>
            </p>
          </div>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Physics engine variants" description="Coverage across parsed assets">
          <VariantsChart />
        </SectionCard>

        <SectionCard title="Catalog growth" description="Cumulative assets by packaging date">
          <GrowthChart />
        </SectionCard>
      </div>

      <SectionCard
        title="Validation signal"
        description="Where attention is needed"
        className="border-destructive/20"
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-4xl font-bold text-destructive tabular-nums">
              {failingReq[1].toLocaleString()}
            </p>
            <p className="text-sm text-muted-foreground">
              occurrences of <strong className="text-foreground">{failingReq[0]}</strong>
            </p>
          </div>
          <Button variant="outline" onClick={() => onNavigate("assets")}>
            Inspect assets
            <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </SectionCard>
    </div>
  );
}

function ValidationView() {
  const rates = stats.validation_feature_rates || {};
  const featureData = useMemo(() =>
    Object.entries(rates)
      .map(([feature, [passed, total]]) => ({
        feature,
        passed: passed as number,
        total: total as number,
        rate: total > 0 ? (passed as number) / (total as number) * 100 : 0,
      }))
      .sort((a, b) => b.rate - a.rate),
    [rates]
  );

  const failingReqs = stats.failing_requirements_top || [];

  return (
    <div className="space-y-6">
      <Tabs defaultValue="rates" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="rates">Pass rates by feature</TabsTrigger>
          <TabsTrigger value="fails">Failing requirements</TabsTrigger>
        </TabsList>

        <TabsContent value="rates" className="mt-4">
          <SectionCard title="Validation pass rates" description="Feature-level results across the catalog">
            <ValidationPassRatesChart />
          </SectionCard>
        </TabsContent>

        <TabsContent value="fails" className="mt-4">
          <SectionCard title="Top failing requirements" description="Most frequent validation failures">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[60%]">Requirement</TableHead>
                    <TableHead className="text-right w-[20%]">Occurrences</TableHead>
                    <TableHead className="text-right w-[20%]">% of failures</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {failingReqs.map(([name, count], index) => (
                    <TableRow key={name}>
                      <TableCell>
                        <code className="text-sm font-mono">{name}</code>
                      </TableCell>
                      <TableCell className="text-right font-mono tabular-nums">
                        {count.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right font-mono tabular-nums">
                        {stats.n_assets > 0
                          ? ((count as number) / stats.n_assets * 100).toFixed(1) + "%"
                          : "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </SectionCard>

          <SectionCard
            title="Assets with failing features"
            description={`${typedAssets.filter((a) => !a.all_features_passed).length} of ${formatNumber(stats.n_assets)} assets have at least one failing feature`}
          >
            <AssetFailureTable />
          </SectionCard>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function AssetFailureTable() {
  const failList = typedAssets.filter((a) => !a.all_features_passed);
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: "asc" | "desc" }>({
    key: "asset",
    direction: "asc",
  });

  const sorted = useMemo(() => {
    return [...failList].sort((a, b) => {
      const aVal = a[sortConfig.key as keyof Asset];
      const bVal = b[sortConfig.key as keyof Asset];
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortConfig.direction === "asc" ? comparison : -comparison;
    });
  }, [failList, sortConfig]);

  const handleSort = (key: string) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  };

  const SortableHeader = ({
    children,
    sortKey,
    className,
  }: {
    children: React.ReactNode;
    sortKey: string;
    className?: string;
  }) => (
    <TableHead
      className={cn("cursor-pointer select-none hover:bg-muted/50", className)}
      onClick={() => handleSort(sortKey)}
    >
      <div className="flex items-center gap-1">
        {children}
        {sortConfig.key === sortKey && (
          sortConfig.direction === "asc" ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3 rotate-180" />
          )
        )}
      </div>
    </TableHead>
  );

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHeader sortKey="asset">Asset</SortableHeader>
            <SortableHeader sortKey="taxonomy_group">Category</SortableHeader>
            <SortableHeader sortKey="mass_kg" className="text-right">Mass</SortableHeader>
            <SortableHeader sortKey="rigid_body_count" className="text-right">Rigid bodies</SortableHeader>
            <TableHead>Validation</TableHead>
            <SortableHeader sortKey="size_total_bytes" className="text-right">Size</SortableHeader>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.slice(0, 200).map((asset) => (
            <TableRow key={asset.asset}>
              <TableCell>
                <div className="flex items-center gap-2">
                  {asset.thumb_url && (
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={asset.thumb_url} alt="" />
                      <AvatarFallback>
                        <Boxes className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                  <span className="font-mono text-sm truncate max-w-[200px]">{asset.asset}</span>
                </div>
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {asset.taxonomy_group || "—"}
              </TableCell>
              <TableCell className="text-right font-mono tabular-nums text-sm">
                {formatMass(asset.mass_kg)}
              </TableCell>
              <TableCell className="text-right font-mono tabular-nums text-sm">
                {formatNumber(asset.rigid_body_count)}
              </TableCell>
              <TableCell>
                <Badge
                  variant={asset.all_features_passed ? "default" : "destructive"}
                  className="text-xs"
                >
                  {asset.features_passed}/{asset.features_total}
                </Badge>
              </TableCell>
              <TableCell className="text-right font-mono tabular-nums text-sm">
                {formatBytes(asset.size_total_bytes)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
        <TableCaption>
          Showing {Math.min(sorted.length, 200)} of {sorted.length} assets with failures
        </TableCaption>
      </Table>
    </div>
  );
}

function AssetsView() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All categories");
  const [status, setStatus] = useState("All");
  const [articulated, setArticulated] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: "asc" | "desc" }>({
    key: "asset",
    direction: "asc",
  });

  const categories = useMemo(() => Object.keys(stats.category_counts).sort(), []);
  const filtered = useMemo(() =>
    typedAssets.filter((asset) =>
      (!query || asset.asset.toLowerCase().includes(query.toLowerCase())) &&
      (category === "All categories" || asset.taxonomy_group === category) &&
      (status === "All" || (status === "Passed" ? asset.all_features_passed : !asset.all_features_passed)) &&
      (!articulated || asset.has_articulation)
    ),
    [query, category, status, articulated]
  );

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      const aVal = a[sortConfig.key as keyof Asset];
      const bVal = b[sortConfig.key as keyof Asset];
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortConfig.direction === "asc" ? comparison : -comparison;
    });
  }, [filtered, sortConfig]);

  const handleSort = (key: string) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  };

  const clearFilters = () => {
    setQuery("");
    setCategory("All categories");
    setStatus("All");
    setArticulated(false);
  };

  const SortableHeader = ({
    children,
    sortKey,
    className,
  }: {
    children: React.ReactNode;
    sortKey: string;
    className?: string;
  }) => (
    <TableHead
      className={cn("cursor-pointer select-none hover:bg-muted/50", className)}
      onClick={() => handleSort(sortKey)}
    >
      <div className="flex items-center gap-1">
        {children}
        {sortConfig.key === sortKey && (
          sortConfig.direction === "asc" ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3 rotate-180" />
          )
        )}
      </div>
    </TableHead>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Asset library</h2>
          <p className="text-sm text-muted-foreground">
            {filtered.length.toLocaleString()} matching records
          </p>
        </div>
        <Button variant="outline" onClick={clearFilters} className="whitespace-nowrap">
          <X className="mr-2 h-4 w-4" />
          Clear filters
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search asset names…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-9"
            aria-label="Search assets"
          />
        </div>
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-full sm:w-[200px]">
            <SelectValue placeholder="All categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All categories">All categories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-full sm:w-[140px]">
            <SelectValue placeholder="All" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            <SelectItem value="Passed">Passed</SelectItem>
            <SelectItem value="Failed">Failed</SelectItem>
          </SelectContent>
        </Select>
        <label className="flex items-center gap-2 whitespace-nowrap">
          <Checkbox
            checked={articulated}
            onCheckedChange={(checked) => setArticulated(checked as boolean)}
          />
          <span className="text-sm">Articulated only</span>
        </label>
      </div>

      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <SortableHeader sortKey="asset">Asset</SortableHeader>
              <SortableHeader sortKey="taxonomy_group">Category</SortableHeader>
              <SortableHeader sortKey="mass_kg" className="text-right">Mass</SortableHeader>
              <SortableHeader sortKey="rigid_body_count" className="text-right">Rigid bodies</SortableHeader>
              <TableHead>Validation</TableHead>
              <SortableHeader sortKey="size_total_bytes" className="text-right">Size</SortableHeader>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.slice(0, 500).map((asset) => (
              <TableRow
                key={asset.asset}
                onClick={() => setSelectedAsset(asset)}
                className={cn(
                  "cursor-pointer hover:bg-muted/50 transition-colors",
                  selectedAsset?.asset === asset.asset && "bg-primary/10"
                )}
              >
                <TableCell>
                  <div className="flex items-center gap-2">
                    {asset.thumb_url && (
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={asset.thumb_url} alt="" />
                        <AvatarFallback>
                          <Boxes className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                    <span className="font-mono text-sm truncate max-w-[200px]">{asset.asset}</span>
                  </div>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {asset.taxonomy_group || "—"}
                </TableCell>
                <TableCell className="text-right font-mono tabular-nums text-sm">
                  {formatMass(asset.mass_kg)}
                </TableCell>
                <TableCell className="text-right font-mono tabular-nums text-sm">
                  {formatNumber(asset.rigid_body_count)}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={asset.all_features_passed ? "default" : "destructive"}
                    className="text-xs"
                  >
                    {asset.features_passed}/{asset.features_total}
                  </Badge>
                </TableCell>
                <TableCell className="text-right font-mono tabular-nums text-sm">
                  {formatBytes(asset.size_total_bytes)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
          <TableCaption>
            Showing {Math.min(sorted.length, 500)} of {sorted.length} assets
          </TableCaption>
        </Table>
      </div>

      {selectedAsset && (
        <AssetDetailSheet asset={selectedAsset} onClose={() => setSelectedAsset(null)} />
      )}
    </div>
  );
}

function AssetDetailSheet({ asset, onClose }: { asset: Asset; onClose: () => void }) {
  return (
    <Sheet open={true} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:w-96 lg:w-[480px] p-0 flex flex-col h-full">
        <SheetHeader className="px-6 py-4 border-b flex-shrink-0">
          <SheetTitle className="text-lg truncate">{asset.asset}</SheetTitle>
          <SheetDescription className="text-sm">
            {asset.asset_type || "Unclassified"} · {asset.taxonomy_group || "No category"}
          </SheetDescription>
        </SheetHeader>
        <ScrollArea className="flex-1 min-h-0 px-6">
          <div className="space-y-4 pt-4 pb-4">
            {/* Thumbnail */}
            {asset.thumb_url ? (
              <div className="relative aspect-video rounded-xl overflow-hidden border border-border bg-muted">
                <img
                  src={asset.thumb_url}
                  alt={asset.asset}
                  className="w-full h-full object-contain"
                />
              </div>
            ) : (
              <div className="relative aspect-video rounded-xl border border-border bg-muted flex items-center justify-center">
                <Boxes className="h-16 w-16 text-muted-foreground/50" />
              </div>
            )}

            {/* Metadata Grid */}
            <dl className="space-y-4 text-sm">
              <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-3">
                <dt className="text-muted-foreground font-medium">Package</dt>
                <dd className="font-mono text-xs truncate max-w-full">{asset.package_id || "—"}</dd>

                <dt className="text-muted-foreground font-medium">Packaged</dt>
                <dd>{asset.packaged_date || "—"}</dd>

                <dt className="text-muted-foreground font-medium">Mass</dt>
                <dd className="font-mono tabular-nums">{formatMass(asset.mass_kg)}</dd>

                <dt className="text-muted-foreground font-medium">Physics variants</dt>
                <dd>
                  <div className="flex flex-wrap gap-1.5">
                    {(asset.variants as string[]).map((v) => (
                      <Badge key={v} variant="secondary" className="text-xs px-2 py-0.5">
                        {v}
                      </Badge>
                    ))}
                  </div>
                </dd>

                <dt className="text-muted-foreground font-medium">Rigid bodies</dt>
                <dd className="font-mono tabular-nums">{formatNumber(asset.rigid_body_count)}</dd>

                <dt className="text-muted-foreground font-medium">Articulated</dt>
                <dd>
                  <Badge variant={asset.has_articulation ? "default" : "secondary"} className="text-xs">
                    {asset.has_articulation ? "Yes" : "No"}
                  </Badge>
                </dd>

                <dt className="text-muted-foreground font-medium">Joint types</dt>
                <dd className="font-mono text-xs font-light bg-muted/50 px-2 py-1 rounded text-wrap break-all">
                  {asset.joint_types || "{}"}
                </dd>

                <dt className="text-muted-foreground font-medium">Conformance</dt>
                <dd className="font-mono text-xs">
                  {asset.conformance_profile || "—"}{" "}
                  {asset.conformance_versions || ""}
                </dd>

                <dt className="text-muted-foreground font-medium">Validation</dt>
                <dd>
                  <Badge
                    variant={asset.all_features_passed ? "default" : "destructive"}
                    className="text-xs px-2 py-0.5"
                  >
                    {asset.features_passed}/{asset.features_total}
                  </Badge>
                </dd>

                <dt className="text-muted-foreground font-medium">Geometry</dt>
                <dd className="font-mono tabular-nums">{formatBytes(asset.geometry_size_bytes)}</dd>

                <dt className="text-muted-foreground font-medium">Textures</dt>
                <dd className="font-mono tabular-nums">{formatBytes(asset.texture_size_bytes)}</dd>

                <dt className="text-muted-foreground font-medium">Source assets</dt>
                <dd className="font-mono tabular-nums">{formatBytes(asset.source_asset_size_bytes)}</dd>

                <dt className="text-muted-foreground font-medium">Provenance</dt>
                <dd className="truncate max-w-full">{asset.provenance_tool || "—"}</dd>
              </div>
            </dl>

            {/* Sizes Summary */}
            <div className="rounded-lg border border-border bg-muted/50 p-4 space-y-2">
              <h4 className="text-sm font-semibold text-foreground">Download sizes</h4>
              <dl className="grid grid-cols-2 gap-2 text-xs">
                <dt className="text-muted-foreground">Total</dt>
                <dd className="font-mono tabular-nums text-right">{formatBytes(asset.size_total_bytes)}</dd>
                <dt className="text-muted-foreground">Payload</dt>
                <dd className="font-mono tabular-nums text-right">{formatBytes(asset.size_payload_bytes)}</dd>
                <dt className="text-muted-foreground">Metadata</dt>
                <dd className="font-mono tabular-nums text-right">{formatBytes(asset.metadata_size_bytes)}</dd>
              </dl>
            </div>
          </div>
        </ScrollArea>

        {/* Footer Actions */}
        <div className="border-t px-6 py-4 bg-background/50 backdrop-blur-sm flex-shrink-0">
          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" onClick={onClose}>
              Close
            </Button>
            <Button
              variant="default"
              className="flex-1"
              onClick={() => {
                window.open(
                  `https://huggingface.co/datasets/nvidia/simready-assets/tree/main/${asset.asset}`,
                  "_blank"
                );
              }}
            >
              <ExternalLink className="mr-2 h-4 w-4" />
              Open on HF
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

function About() {
  return (
    <div className="max-w-3xl space-y-6">
      <SectionCard title="About this catalog" description="Community-built catalog for NVIDIA SimReady Assets">
        <p className="text-sm text-muted-foreground mb-4">
          This portal indexes NVIDIA SimReady Assets with physics, packaging, conformance, and validation metadata.
        </p>
        <p className="text-sm text-muted-foreground mb-4">
          The underlying assets are © NVIDIA Corporation, licensed{" "}
          <a href="https://creativecommons.org/licenses/by/4.0/" className="underline hover:text-foreground" target="_blank">
            CC-BY-4.0
          </a>
          . Thumbnails are served from the original Hugging Face dataset.
        </p>
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>
            <strong>Data catalog and pipeline:</strong>{" "}
            <a href="https://github.com/nvidia/simready-assets" className="underline hover:text-foreground" target="_blank">
              Companion dataset
            </a>
          </p>
          <p>
            <strong>Validation terminology:</strong>{" "}
            <a href="https://github.com/NVIDIA/simready-foundation" className="underline hover:text-foreground" target="_blank">
              simready-foundation
            </a>
          </p>
          <p>
            <strong>Assets referenced via hotlinked thumbnails served from the HF dataset</strong>
          </p>
        </div>
        <a
          href="https://huggingface.co/datasets/nvidia/simready-assets"
          target="_blank"
          className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline mt-4"
        >
          Open the dataset
          <ExternalLink className="h-4 w-4" />
        </a>
      </SectionCard>

      <SectionCard title="Data snapshot" description={`Catalog data as of ${stats.as_of}`}>
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
          <dt className="text-muted-foreground">Assets</dt>
          <dd className="font-mono tabular-nums">{formatNumber(stats.n_assets)}</dd>
          <dt className="text-muted-foreground">Total size</dt>
          <dd>{stats.total_size_gb} GB</dd>
          <dt className="text-muted-foreground">Files</dt>
          <dd className="font-mono tabular-nums">{formatNumber(stats.n_files)}</dd>
          <dt className="text-muted-foreground">Categories</dt>
          <dd>{formatNumber(stats.n_categories)}</dd>
          <dt className="text-muted-foreground">Articulated</dt>
          <dd>{formatNumber(stats.articulated_count)} ({stats.articulated_pct}%)</dd>
          <dt className="text-muted-foreground">Validation pass rate</dt>
          <dd>{stats.validation_pass_rate}%</dd>
        </dl>
      </SectionCard>
    </div>
  );
}

export default function Home() {
  const [view, setView] = useState<View>("overview");

  const navItems: { id: View; label: string; icon: React.ReactNode; count?: number }[] = [
    { id: "overview", label: "Overview", icon: <LayoutDashboard className="h-4 w-4" /> },
    { id: "assets", label: "Assets", icon: <Boxes className="h-4 w-4" />, count: typedAssets.length },
    { id: "validation", label: "Validation", icon: <ShieldCheck className="h-4 w-4" /> },
    { id: "about", label: "About", icon: <CircleHelp className="h-4 w-4" /> },
  ];

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background">
        <div className="flex">
          <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:border-r lg:border-border lg:bg-card lg:min-h-screen lg:sticky lg:top-0">
            <div className="flex h-16 items-center px-6 border-b border-border">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-lg">
                  S
                </div>
                <span className="font-semibold">SimReady Explorer</span>
              </div>
            </div>
            <nav className="flex-1 p-4 space-y-1" aria-label="Main navigation">
              {navItems.map((item) => (
                <Button
                  key={item.id}
                  variant={view === item.id ? "default" : "ghost"}
                  className="w-full justify-start gap-3 text-sm"
                  onClick={() => setView(item.id)}
                >
                  {item.icon}
                  <span>{item.label}</span>
                  {item.count && (
                    <Badge variant="secondary" className="ml-auto text-xs">
                      {item.count.toLocaleString()}
                    </Badge>
                  )}
                </Button>
              ))}
              <Separator className="my-4" />
              <div className="text-xs text-muted-foreground px-2">
                Catalog snapshot
              </div>
              <div className="font-mono tabular-nums text-sm px-2">{stats.as_of}</div>
              <a
                href="https://huggingface.co/datasets/nvidia/simready-assets"
                target="_blank"
                className="flex items-center gap-2 px-2 py-2 text-sm text-primary hover:underline mt-2"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                Open dataset
              </a>
            </nav>
          </aside>

          <main className="flex-1 min-w-0">
            <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
              <div className="flex h-16 items-center justify-between px-6">
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    SimReady catalog
                  </p>
                  <h1 className="text-xl font-semibold">
                    {view === "overview"
                      ? "Catalog overview"
                      : view.charAt(0).toUpperCase() + view.slice(1)}
                  </h1>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="gap-1">
                    <Activity className="h-3 w-3" />
                    Catalog ready
                  </Badge>
                  <a
                    href="https://huggingface.co/datasets/nvidia/simready-assets"
                    target="_blank"
                    className="hidden sm:flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-primary hover:underline"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    Dataset
                  </a>
                </div>
              </div>
            </header>

            <div className="p-6 space-y-6 max-w-7xl mx-auto">
              {view === "overview" && <Overview onNavigate={setView} />}
              {view === "assets" && <AssetsView />}
              {view === "validation" && <ValidationView />}
              {view === "about" && <About />}
            </div>
          </main>
        </div>
      </div>
    </TooltipProvider>
  );
}