import pygame



class GameDisplay:
    def __init__(self, width: int, height: int, heatmapPath: str, display_index: int = 0):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN, display=display_index)
        self.heatmapPath = heatmapPath
        self.running = True

    def clear(self):
        self.screen.fill((0, 0, 0))

    def update(self):
        try:
            heatmap_image = pygame.image.load(self.heatmapPath)
            self.screen.blit(heatmap_image, (self.width//2, 0))
            pygame.display.flip()
        except FileNotFoundError:
            self.screen.fill((255, 0, 0))
            pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False