import { Rail } from "@/components/shell/Rail";
import { TopBar } from "@/components/shell/TopBar";
import { EmberPanel } from "@/features/tutor/EmberPanel";

export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-screen">
      <Rail />
      <TopBar />
      <main className="md:pl-[72px]">{children}</main>
      <EmberPanel />
    </div>
  );
}
