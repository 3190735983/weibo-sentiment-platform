import { defineStore } from 'pinia'
import { ref } from 'vue'
import { topicApi } from '../api'

export const useTopicStore = defineStore('topic', () => {
    const topics = ref([])
    const currentTopic = ref(null)
    const loading = ref(false)

    // 获取话题列表
    async function fetchTopics() {
        loading.value = true
        try {
            const res = await topicApi.getTopics()
            if (res.success) {
                topics.value = res.data
            }
        } catch (error) {
            console.error('Failed to fetch topics:', error)
        } finally {
            loading.value = false
        }
    }

    // 设置当前话题
    function setCurrentTopic(topic) {
        currentTopic.value = topic
    }

    // 添加话题
    async function addTopic(topicData) {
        try {
            const res = await topicApi.createTopic(topicData)
            if (res.success) {
                await fetchTopics()
                return res.data
            }
        } catch (error) {
            console.error('Failed to add topic:', error)
            throw error
        }
    }

    // 更新话题
    async function updateTopic(id, topicData) {
        try {
            const res = await topicApi.updateTopic(id, topicData)
            if (res.success) {
                await fetchTopics()
                return res.data
            }
        } catch (error) {
            console.error('Failed to update topic:', error)
            throw error
        }
    }

    // 删除话题
    async function deleteTopic(id) {
        try {
            const res = await topicApi.deleteTopic(id)
            if (res.success) {
                await fetchTopics()
            }
        } catch (error) {
            console.error('Failed to delete topic:', error)
            throw error
        }
    }

    return {
        topics,
        currentTopic,
        loading,
        fetchTopics,
        setCurrentTopic,
        addTopic,
        updateTopic,
        deleteTopic
    }
})
