import asyncio

async def youtube_parser():
    web.get('https://www.youtube.com/channel/UCMLajX5RcAKB1N3sRELMA2g/videos')

    videos = web.find_elements_by_id('video-title')
    for i in range(len(videos)):
        print(videos[i].get_attribute('href'))

    await asyncio.sleep(1)
    web.quit()
