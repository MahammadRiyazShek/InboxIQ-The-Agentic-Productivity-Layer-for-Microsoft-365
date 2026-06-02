import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Card, CardHeader, Body1, Title2, Badge, Button, Spinner,
} from "@fluentui/react-components";

interface Briefing {
  summary: string;
  urgent_count: number;
  action_items: string[];
  meetings_today: Array<{ subject: string; start: string }>;
  audio_url: string | null;
}

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function Dashboard() {
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/briefing/me`).then((r) => {
      setBriefing(r.data); setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <Spinner label="Loading your briefing…" />;

  return (
    <div style={{ padding: 32, maxWidth: 980, margin: "0 auto" }}>
      <Title2>Good morning ☀️</Title2>
      <Body1>{briefing?.summary}</Body1>

      <Card style={{ marginTop: 24 }}>
        <CardHeader header={<b>Today's Action Items</b>} />
        <ul>
          {briefing?.action_items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </Card>

      <Card style={{ marginTop: 16 }}>
        <CardHeader
          header={<b>Urgent</b>}
          description={<Badge appearance="filled" color="danger">
            {briefing?.urgent_count}
          </Badge>}
        />
      </Card>

      <Button appearance="primary" style={{ marginTop: 24 }}>
        Run Triage Now
      </Button>
    </div>
  );
}
