import { describe, expect, it } from 'vitest'

import {
  CHINA_MAP_APPROVAL_NUMBER,
  CHINA_MAP_SOURCE_NAME,
  CHINA_MAP_SOURCE_URL,
  getChinaMapGeoJson,
} from './chinaMapSource'

describe('chinaMapSource', () => {
  it('uses Tianditu approved GeoJSON instead of the Aliyun source', () => {
    const geoJson = getChinaMapGeoJson()

    expect(CHINA_MAP_SOURCE_NAME).toBe('天地图服务中心')
    expect(CHINA_MAP_SOURCE_URL).toBe('https://cloudcenter.tianditu.gov.cn/administrativeDivision')
    expect(CHINA_MAP_APPROVAL_NUMBER).toBe('GS（2024）0650号')
    expect(geoJson.type).toBe('FeatureCollection')
  })
})
