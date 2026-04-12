<template>
  <div v-if="isMobile && open" class="inspector-backdrop" @click="$emit('close')"></div>
  <aside class="inspector-panel" :class="{ open, mobile: isMobile, closed: !open && !isMobile }">
    <div class="inspector-header">
      <div>
        <p class="panel-eyebrow">Run Inspector</p>
        <h2>推理与工具轨迹</h2>
      </div>
      <button v-if="isMobile" class="close-btn" type="button" @click="$emit('close')">关闭</button>
    </div>

    <section class="summary-grid">
      <article class="summary-card">
        <span>运行模式</span>
        <strong>{{ runModeLabel }}</strong>
      </article>
      <article class="summary-card">
        <span>解析模式</span>
        <strong>{{ agentResult?.parse_mode || '等待结果' }}</strong>
      </article>
      <article class="summary-card">
        <span>工具调用</span>
        <strong>{{ toolCount }}</strong>
      </article>
      <article class="summary-card">
        <span>知识命中</span>
        <strong>{{ evidenceCount }}</strong>
      </article>
      <article class="summary-card">
        <span>置信度</span>
        <strong>{{ confidenceText }}</strong>
      </article>
      <article class="summary-card">
        <span>连接状态</span>
        <strong>{{ connectionLabel }}</strong>
      </article>
    </section>

    <section class="inspector-section">
      <div class="section-title">本轮摘要</div>
      <div class="summary-text">
        {{ agentResult?.summary || (loading ? '本轮正在运行，等待摘要生成…' : '发起一次对话后，这里会展示本轮摘要。') }}
      </div>
    </section>

    <section class="inspector-section">
      <div class="section-title">思考轨迹</div>
      <div v-if="thoughtEntries.length" class="timeline-list">
        <article v-for="item in thoughtEntries" :key="item.id" class="timeline-card">
          <div class="timeline-meta">
            <span>思考</span>
            <small>{{ item.time }}</small>
          </div>
          <p>{{ item.title }}</p>
        </article>
      </div>
      <div v-else class="placeholder-text">本轮还没有记录到思考轨迹。</div>
    </section>

    <section class="inspector-section">
      <div class="section-title">工具调用</div>
      <div v-if="toolEntries.length" class="timeline-list">
        <article v-for="item in toolEntries" :key="item.id" class="timeline-card">
          <div class="timeline-meta">
            <span>{{ item.title }}</span>
            <small>{{ item.time }}</small>
          </div>
          <p v-if="item.input"><strong>输入：</strong>{{ item.input }}</p>
          <p v-if="item.output"><strong>输出：</strong>{{ item.output }}</p>
        </article>
      </div>
      <div v-else class="placeholder-text">当前没有工具调用记录。</div>
    </section>

    <section class="inspector-section">
      <div class="section-title">知识命中</div>
      <div v-if="normalizedEvidence.length" class="evidence-list">
        <article v-for="(item, index) in normalizedEvidence" :key="`${item.title}-${index}`" class="evidence-card">
          <div class="evidence-head">
            <strong>{{ item.title }}</strong>
            <span>{{ item.scoreText }}</span>
          </div>
          <p>{{ item.snippet }}</p>
        </article>
      </div>
      <div v-else class="placeholder-text">本轮没有命中知识库证据。</div>
    </section>

    <section class="inspector-section">
      <div class="section-title">展示卡片</div>
      <div v-if="displayCards.length" class="display-card-list">
        <button
          v-for="(card, index) in displayCards"
          :key="`${card.title || card.type || 'card'}-${index}`"
          class="display-card-button"
          type="button"
          @click="openDisplayCard(card)"
        >
          <div class="display-card-head">
            <strong>{{ card.title || displayTypeLabel(card.type) }}</strong>
            <span>{{ displayPlacementLabel(card.placement) }}</span>
          </div>
          <p>{{ card.subtitle || displayTypeLabel(card.type) }}</p>
        </button>
      </div>
      <div v-else class="placeholder-text">当前没有可展示的图谱或数据卡片。</div>
    </section>
  </aside>

  <teleport to="body">
    <div v-if="activeModalCard" class="display-modal-overlay" @click.self="closeDisplayPanels">
      <div class="display-modal">
        <div class="display-shell-header">
          <div>
            <p class="panel-eyebrow">Display Card</p>
            <h3>{{ activeModalCard.title || displayTypeLabel(activeModalCard.type) }}</h3>
          </div>
          <button class="display-close-btn" type="button" @click="closeDisplayPanels">关闭</button>
        </div>
        <div class="display-shell-body">
          <KnowledgeGraphPanel
            v-if="activeModalCard.type === 'knowledge_graph'"
            :content="activeModalCard.payload?.content || ''"
            :nodes="activeModalCard.payload?.nodes || []"
            :links="activeModalCard.payload?.links || []"
            :dynamic-payload="activeModalCard.payload?.dynamic_payload || {}"
            :visual-config="activeModalCard.payload?.visual_config || {}"
          />
          <div v-else class="display-fallback">暂不支持该弹窗卡片类型。</div>
        </div>
      </div>
    </div>

    <div v-if="activeDrawerCard" class="display-drawer-backdrop" @click="closeDisplayPanels"></div>
    <aside v-if="activeDrawerCard" class="display-drawer" :class="{ mobile: isMobile }">
      <div class="display-shell-header">
        <div>
          <p class="panel-eyebrow">Display Card</p>
          <h3>{{ activeDrawerCard.title || displayTypeLabel(activeDrawerCard.type) }}</h3>
        </div>
        <button class="display-close-btn" type="button" @click="closeDisplayPanels">关闭</button>
      </div>
      <div class="display-shell-body drawer-body">
        <template v-if="activeDrawerCard.type === 'original_text'">
          <a
            v-if="activeDrawerCard.payload?.file_url"
            class="display-file-link"
            :href="activeDrawerCard.payload.file_url"
            target="_blank"
            rel="noreferrer"
          >
            查看原文件
          </a>
          <pre class="display-pre">{{ activeDrawerCard.payload?.content || '暂无内容' }}</pre>
        </template>

        <template v-else-if="activeDrawerCard.type === 'table'">
          <div class="display-table-wrap">
            <table class="display-table">
              <thead>
                <tr>
                  <th v-for="column in activeDrawerCard.payload?.columns || []" :key="column.key">
                    {{ column.label || column.key }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rowIndex) in activeDrawerCard.payload?.rows || []" :key="rowIndex">
                  <td v-for="column in activeDrawerCard.payload?.columns || []" :key="column.key">
                    {{ formatDisplayValue(row?.[column.key]) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <template v-else-if="activeDrawerCard.type === 'metric_board'">
          <div class="display-metric-grid">
            <article
              v-for="(item, index) in activeDrawerCard.payload?.items || []"
              :key="`${item.label || 'metric'}-${index}`"
              class="display-metric-item"
            >
              <span>{{ item.label || '指标' }}</span>
              <strong>{{ item.value }}{{ item.unit || '' }}</strong>
            </article>
          </div>
        </template>

        <template v-else>
          <div class="display-fallback">暂不支持该侧栏卡片类型。</div>
        </template>
      </div>
    </aside>
  </teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import KnowledgeGraphPanel from '@/components/Home/KnowledgeGraphPanel.vue';

const props = defineProps({
  open: { type: Boolean, default: true },
  isMobile: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  runMode: { type: String, default: 'agent' },
  connectionState: { type: String, default: 'disconnected' },
  agentResult: { type: Object, default: null },
  traceTimeline: {
    type: Array,
    default: () => [],
  },
});

defineEmits(['close']);

const activeModalCard = ref(null);
const activeDrawerCard = ref(null);
const lastAutoOpenSignature = ref('');

const runModeLabel = computed(() => (props.runMode === 'chat' ? 'Chat' : 'Agent'));
const toolEntries = computed(() => props.traceTimeline.filter((item) => item.kind === 'tool'));
const thoughtEntries = computed(() => props.traceTimeline.filter((item) => item.kind === 'thought'));
const toolCount = computed(() => props.agentResult?.tool_calls?.length || toolEntries.value.length || 0);
const evidenceCount = computed(() => props.agentResult?.evidence?.length || 0);
const displayCards = computed(() =>
  Array.isArray(props.agentResult?.display_cards) ? props.agentResult.display_cards : []
);

const confidenceText = computed(() => {
  const value = props.agentResult?.confidence;
  return typeof value === 'number' ? `${Math.round(value * 100)}%` : '待生成';
});

const connectionLabel = computed(() => {
  if (props.connectionState === 'ready') return '已连接';
  if (props.connectionState === 'connecting') return '连接中';
  if (props.connectionState === 'error') return '异常';
  return '未连接';
});

const normalizedEvidence = computed(() =>
  (props.agentResult?.evidence || []).map((item) => ({
    title: item.title || item.source || item.category || '知识条目',
    snippet: item.snippet || item.content || '暂无片段',
    scoreText: typeof item.score === 'number' ? `相似度 ${item.score.toFixed(3)}` : '相似度待定',
  }))
);

const displayTypeLabel = (type) => {
  const mapping = {
    knowledge_graph: '知识图谱',
    original_text: '原文预览',
    table: '结果表格',
    metric_board: '指标看板',
  };
  return mapping[String(type || '')] || '展示卡片';
};

const displayPlacementLabel = (placement) =>
  String(placement || 'modal') === 'right_drawer' ? '侧栏' : '弹窗';

const closeDisplayPanels = () => {
  activeModalCard.value = null;
  activeDrawerCard.value = null;
};

const selectPrimaryDisplayCard = (cards) => {
  if (!Array.isArray(cards) || !cards.length) return null;
  return cards.find((card) => card?.type === 'knowledge_graph') || cards[0] || null;
};

const openDisplayCard = (card) => {
  closeDisplayPanels();
  const placement = String(card?.placement || 'modal');
  if (placement === 'right_drawer' && card?.type !== 'knowledge_graph') {
    activeDrawerCard.value = card;
    return;
  }
  activeModalCard.value = card;
};

const formatDisplayValue = (value) => {
  if (value === null || value === undefined || value === '') return '-';
  if (Array.isArray(value)) return value.join('、');
  if (typeof value === 'object') return JSON.stringify(value, null, 2);
  return String(value);
};

watch(
  () => props.agentResult,
  (result) => {
    const cards = Array.isArray(result?.display_cards) ? result.display_cards : [];
    if (!cards.length) {
      lastAutoOpenSignature.value = '';
      closeDisplayPanels();
      return;
    }

    const signature = JSON.stringify(cards);
    if (signature === lastAutoOpenSignature.value) return;

    lastAutoOpenSignature.value = signature;
    closeDisplayPanels();

    const primaryCard = selectPrimaryDisplayCard(cards);
    if (primaryCard) openDisplayCard(primaryCard);
  },
  { deep: true }
);
</script>

<style scoped>
.inspector-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 18, 34, 0.24);
  backdrop-filter: blur(6px);
  z-index: 59;
}

.inspector-panel,
.inspector-panel * {
  transition-property: background, background-color, border-color, color, box-shadow, opacity, filter;
  transition-duration: 0.45s;
  transition-timing-function: ease;
}

.inspector-panel {
  position: relative;
  z-index: 60;
  display: flex;
  flex-direction: column;
  gap: 18px;
  width: 360px;
  min-height: 0;
  padding: 22px 18px 18px;
  border-radius: 30px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.6)),
    linear-gradient(150deg, rgba(131, 180, 255, 0.14), rgba(255, 255, 255, 0));
  border: 1px solid rgba(255, 255, 255, 0.65);
  box-shadow:
    0 28px 60px rgba(14, 30, 62, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(18px);
  overflow: auto;
  transition:
    transform 0.55s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.45s ease,
    width 0.45s ease,
    padding 0.45s ease,
    margin 0.45s ease,
    background 0.45s ease,
    border-color 0.45s ease,
    box-shadow 0.45s ease;
}

.inspector-panel.closed {
  width: 0;
  padding-left: 0;
  padding-right: 0;
  opacity: 0;
  overflow: hidden;
  transform: translateX(24px);
  pointer-events: none;
  border-color: transparent;
  box-shadow: none;
}

.inspector-panel.mobile {
  position: fixed;
  top: 12px;
  right: 12px;
  bottom: 12px;
  max-width: min(88vw, 380px);
  transform: translateX(112%);
  transition: transform 0.32s ease;
}

.inspector-panel.mobile.open {
  transform: translateX(0);
}

.inspector-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.panel-eyebrow,
.inspector-header h2 {
  margin: 0;
}

.panel-eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(17, 39, 76, 0.48);
}

.inspector-header h2,
.display-shell-header h3 {
  margin-top: 6px;
  font-size: 20px;
  line-height: 1.2;
  color: #10213f;
}

.close-btn,
.display-close-btn {
  border: none;
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(17, 39, 76, 0.06);
  color: #173159;
  cursor: pointer;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.summary-card,
.timeline-card,
.evidence-card,
.summary-text,
.display-card-button {
  background: rgba(255, 255, 255, 0.62);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.58);
}

.summary-card {
  padding: 14px;
}

.summary-card span,
.summary-card strong {
  display: block;
}

.summary-card span {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(17, 39, 76, 0.46);
}

.summary-card strong {
  margin-top: 8px;
  font-size: 15px;
  color: #11274c;
}

.inspector-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #14305a;
}

.summary-text,
.timeline-card,
.evidence-card {
  padding: 14px;
  color: #173159;
}

.summary-text,
.timeline-card p,
.evidence-card p,
.placeholder-text,
.display-card-button p {
  font-size: 13px;
  line-height: 1.75;
}

.timeline-list,
.evidence-list,
.display-card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-meta,
.evidence-head,
.display-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.timeline-meta span,
.evidence-head strong,
.display-card-head strong {
  font-size: 13px;
  font-weight: 700;
}

.timeline-meta small,
.evidence-head span,
.display-card-head span {
  font-size: 11px;
  color: rgba(23, 49, 89, 0.56);
}

.timeline-card p,
.evidence-card p,
.display-card-button p {
  margin: 10px 0 0;
  word-break: break-word;
  white-space: pre-wrap;
}

.display-card-button {
  padding: 14px;
  text-align: left;
}

.placeholder-text {
  padding: 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.52);
  color: rgba(23, 49, 89, 0.58);
}

.display-modal-overlay,
.display-drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 18, 34, 0.34);
  backdrop-filter: blur(10px);
}

.display-modal-overlay {
  z-index: 120;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.display-drawer-backdrop {
  z-index: 119;
}

.display-modal,
.display-drawer {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(247, 250, 255, 0.9)),
    linear-gradient(150deg, rgba(131, 180, 255, 0.16), rgba(255, 255, 255, 0));
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow:
    0 28px 60px rgba(14, 30, 62, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.78);
}

.display-modal {
  width: min(96vw, 1360px);
  height: min(90vh, 980px);
  border-radius: 28px;
  overflow: hidden;
}

.display-drawer {
  position: fixed;
  top: 18px;
  right: 18px;
  bottom: 18px;
  z-index: 121;
  width: min(42vw, 560px);
  border-radius: 28px;
  display: flex;
  flex-direction: column;
}

.display-drawer.mobile {
  left: 12px;
  right: 12px;
  top: 12px;
  bottom: 12px;
  width: auto;
}

.display-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid rgba(135, 168, 224, 0.18);
}

.display-shell-body {
  height: calc(100% - 88px);
  overflow: auto;
}

.drawer-body {
  padding: 18px 20px 20px;
}

.display-file-link {
  display: inline-flex;
  margin-bottom: 12px;
  color: #1e63d7;
  text-decoration: none;
  font-weight: 700;
}

.display-pre {
  margin: 0;
  padding: 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.64);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.8;
  color: #173159;
}

.display-table-wrap {
  overflow: auto;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.64);
}

.display-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 420px;
}

.display-table th,
.display-table td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid rgba(135, 168, 224, 0.14);
  font-size: 13px;
  color: #173159;
  vertical-align: top;
}

.display-table th {
  position: sticky;
  top: 0;
  background: rgba(244, 248, 255, 0.96);
  font-weight: 700;
}

.display-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.display-metric-item {
  padding: 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.64);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.display-metric-item span {
  font-size: 12px;
  color: rgba(23, 49, 89, 0.58);
}

.display-metric-item strong {
  font-size: 20px;
  color: #10213f;
}

.display-fallback {
  padding: 24px;
  color: #173159;
}

.display-shell-body :deep(.kg-panel) {
  min-height: 100%;
}

.display-shell-body :deep(.kg-content),
.display-shell-body :deep(.kg-main),
.display-shell-body :deep(.graph-2d-wrapper),
.display-shell-body :deep(.graph-2d),
.display-shell-body :deep(.graph-text),
.display-shell-body :deep(.kg-json) {
  min-height: 720px;
  height: 720px;
}
</style>

<style>
[data-theme='dark'] .inspector-panel {
  background:
    linear-gradient(180deg, rgba(9, 16, 30, 0.94), rgba(8, 14, 26, 0.88)),
    linear-gradient(150deg, rgba(70, 126, 255, 0.14), rgba(34, 150, 139, 0.06) 58%, rgba(255, 255, 255, 0));
  border-color: rgba(118, 156, 255, 0.12);
  box-shadow:
    0 28px 66px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

[data-theme='dark'] .inspector-panel .panel-eyebrow,
[data-theme='dark'] .inspector-panel .timeline-meta small,
[data-theme='dark'] .inspector-panel .evidence-head span,
[data-theme='dark'] .inspector-panel .display-card-head span,
[data-theme='dark'] .inspector-panel .placeholder-text,
[data-theme='dark'] .display-metric-item span {
  color: rgba(237, 244, 255, 0.58);
}

[data-theme='dark'] .inspector-panel .inspector-header h2,
[data-theme='dark'] .inspector-panel .summary-card strong,
[data-theme='dark'] .inspector-panel .section-title,
[data-theme='dark'] .inspector-panel .summary-text,
[data-theme='dark'] .inspector-panel .timeline-card,
[data-theme='dark'] .inspector-panel .evidence-card,
[data-theme='dark'] .inspector-panel .display-card-button,
[data-theme='dark'] .inspector-panel .close-btn,
[data-theme='dark'] .display-shell-header h3,
[data-theme='dark'] .display-close-btn,
[data-theme='dark'] .display-pre,
[data-theme='dark'] .display-table th,
[data-theme='dark'] .display-table td,
[data-theme='dark'] .display-metric-item strong,
[data-theme='dark'] .display-fallback {
  color: #edf4ff;
}

[data-theme='dark'] .inspector-panel .summary-card,
[data-theme='dark'] .inspector-panel .summary-text,
[data-theme='dark'] .inspector-panel .timeline-card,
[data-theme='dark'] .inspector-panel .evidence-card,
[data-theme='dark'] .inspector-panel .display-card-button,
[data-theme='dark'] .inspector-panel .placeholder-text,
[data-theme='dark'] .inspector-panel .close-btn,
[data-theme='dark'] .display-modal,
[data-theme='dark'] .display-drawer,
[data-theme='dark'] .display-pre,
[data-theme='dark'] .display-table-wrap,
[data-theme='dark'] .display-metric-item,
[data-theme='dark'] .display-close-btn {
  background:
    linear-gradient(180deg, rgba(15, 25, 43, 0.92), rgba(12, 20, 34, 0.84)),
    linear-gradient(150deg, rgba(63, 118, 255, 0.08), rgba(40, 188, 172, 0.05));
  border-color: rgba(118, 156, 255, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

[data-theme='dark'] .display-table th {
  background: rgba(16, 26, 44, 0.96);
}
</style>
