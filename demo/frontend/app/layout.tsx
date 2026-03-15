import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Style.re × AI Robotics — Live Demo',
  description: 'Autonomous retail delivery powered by OpenClaw agents + robots',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark h-full">
      <body className="h-full overflow-hidden">{children}</body>
    </html>
  );
}
