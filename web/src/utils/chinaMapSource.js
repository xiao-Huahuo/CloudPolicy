import chinaProvinceGeoJsonRaw from '@/assets/maps/中国_省.geojson?raw'

export const CHINA_MAP_SOURCE_NAME = '天地图服务中心'
export const CHINA_MAP_SOURCE_URL = 'https://cloudcenter.tianditu.gov.cn/administrativeDivision'
export const CHINA_MAP_APPROVAL_NUMBER = 'GS（2024）0650号'

const chinaProvinceGeoJson = JSON.parse(chinaProvinceGeoJsonRaw)

export const getChinaMapGeoJson = () => chinaProvinceGeoJson

export const registerChinaMap = (echartsInstance, mapName = 'china') => {
  if (!echartsInstance.getMap(mapName)) {
    echartsInstance.registerMap(mapName, getChinaMapGeoJson())
  }
}
