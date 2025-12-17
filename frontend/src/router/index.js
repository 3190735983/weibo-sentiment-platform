import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘' }
    },
    {
        path: '/topic/:id',
        name: 'TopicDetail',
        component: () => import('../views/TopicDetail.vue'),
        meta: { title: '话题详情' }
    },
    {
        path: '/manage',
        name: 'DataManage',
        component: () => import('../views/DataManage.vue'),
        meta: { title: '数据管理' }
    },
    {
        path: '/insight',
        name: 'AIInsight',
        component: () => import('../views/AIInsight.vue'),
        meta: { title: 'AI智能洞察' }
    },
    {
        path: '/crawler',
        name: 'CrawlerManagement',
        component: () => import('../views/CrawlerManagement.vue'),
        meta: { title: '爬虫管理' }
    },
    {
        path: '/pipeline',
        name: 'PipelineExecutor',
        component: () => import('../views/PipelineExecutor.vue'),
        meta: { title: 'Pipeline执行' }
    },
    {
        path: '/visualization',
        name: 'DataVisualization',
        component: () => import('../views/DataVisualization.vue'),
        meta: { title: '数据可视化' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    // 设置标题
    document.title = to.meta.title ? `${to.meta.title} - 微博情感分析平台` : '微博情感分析平台'
    next()
})

export default router
