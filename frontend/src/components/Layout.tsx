import { NavLink, Outlet } from "react-router-dom";
import { FileSearch, Files, LayoutDashboard, Upload } from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/upload", label: "Upload", icon: Upload },
  { to: "/documents", label: "Documents", icon: Files },
  { to: "/search", label: "Search", icon: FileSearch }
];

export function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">DL</span>
          <span>DocuLens</span>
        </div>
        <nav>
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink key={link.to} to={link.to}>
                <Icon size={18} />
                {link.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
