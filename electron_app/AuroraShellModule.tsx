import { spawn } from 'child_process';
import { dialog, BrowserWindow } from 'electron';
import fs from 'fs';

export interface NodeContext {
  input?: string;
  data?: any;
}

export interface ExecResult {
  stdout: string;
  stderr: string;
  code: number | null;
}

export abstract class BaseNode {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  abstract run(ctx: NodeContext): Promise<NodeContext>;
}

export class AuroraLLMNode extends BaseNode {
  endpoint: string;
  constructor(id: string, endpoint: string) {
    super(id);
    this.endpoint = endpoint;
  }
  async run(ctx: NodeContext): Promise<NodeContext> {
    const prompt = ctx.input || '';
    const resp = await fetch(this.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'local',
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await resp.json();
    const text = data?.choices?.[0]?.message?.content || '';
    return { input: text };
  }
}

export class AuroraExecNode extends BaseNode {
  constructor(id: string) {
    super(id);
  }
  async confirm(cmd: string): Promise<boolean> {
    if (BrowserWindow.getAllWindows().length) {
      const res = await dialog.showMessageBox({
        type: 'question',
        message: cmd,
        buttons: ['Cancel', 'Run']
      });
      return res.response === 1;
    }
    return true;
  }

  async run(ctx: NodeContext): Promise<NodeContext> {
    const cmd = ctx.input || '';
    const ok = await this.confirm(cmd);
    if (!ok) return { data: { cancelled: true } };
    const result: ExecResult = await new Promise((resolve) => {
      const child = spawn(cmd, { shell: true });
      let stdout = '';
      let stderr = '';
      child.stdout.on('data', d => { stdout += d; });
      child.stderr.on('data', d => { stderr += d; });
      child.on('close', code => {
        resolve({ stdout, stderr, code });
      });
    });
    return { data: result };
  }
}

export class SymbolicNode extends BaseNode {
  symbol: string;
  constructor(id: string, symbol: string) {
    super(id);
    this.symbol = symbol;
  }
  async run(ctx: NodeContext): Promise<NodeContext> {
    console.log('SymbolicNode', this.symbol);
    return ctx;
  }
}

export interface Flow {
  nodes: BaseNode[];
}

export function saveFlow(flow: Flow, path: string): void {
  fs.writeFileSync(path, JSON.stringify(flow, null, 2));
}

export function loadFlow(path: string): Flow {
  return JSON.parse(fs.readFileSync(path, 'utf-8')) as Flow;
}

