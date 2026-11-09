#import <Cocoa/Cocoa.h>

@interface InterfaceLauncher : NSObject <NSApplicationDelegate>
@property NSTask *server;
@property NSString *interfaceURL;
@property NSString *projectPath;
@property NSMutableData *output;
@property BOOL quitting;
@end

@implementation InterfaceLauncher
- (void)showError:(NSString *)message {
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"Não foi possível abrir o Adaptar Vaga";
    alert.informativeText = message;
    [alert addButtonWithTitle:@"Fechar"];
    [alert runModal];
    [NSApp terminate:nil];
}
- (void)openInterface:(id)sender {
    if (self.interfaceURL) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:self.interfaceURL]];
    }
}
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    self.projectPath = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"ProjectPath"];
    NSString *script = [self.projectPath stringByAppendingPathComponent:@"scripts/interface_vagas.py"];
    if (![[NSFileManager defaultManager] fileExistsAtPath:script]) {
        [self showError:@"A pasta do projeto não foi encontrada. O aplicativo depende dos arquivos em Adaptar Vaga."];
        return;
    }
    NSMenu *menu = [[NSMenu alloc] init];
    NSMenuItem *root = [[NSMenuItem alloc] init];
    [menu addItem:root];
    NSMenu *appMenu = [[NSMenu alloc] initWithTitle:@"Adaptar Vaga"];
    NSMenuItem *open = [[NSMenuItem alloc] initWithTitle:@"Abrir interface" action:@selector(openInterface:) keyEquivalent:@"o"];
    open.target = self;
    [appMenu addItem:open];
    [appMenu addItem:[NSMenuItem separatorItem]];
    [appMenu addItem:[[NSMenuItem alloc] initWithTitle:@"Encerrar Adaptar Vaga" action:@selector(terminate:) keyEquivalent:@"q"]];
    root.submenu = appMenu;
    NSApp.mainMenu = menu;

    NSString *python = nil;
    for (NSString *candidate in @[@"/opt/homebrew/bin/python3", @"/usr/local/bin/python3", @"/usr/bin/python3"]) {
        if ([[NSFileManager defaultManager] isExecutableFileAtPath:candidate]) { python = candidate; break; }
    }
    if (!python) { [self showError:@"Python 3 não foi encontrado neste Mac."]; return; }
    self.output = [NSMutableData data];
    self.server = [[NSTask alloc] init];
    self.server.executableURL = [NSURL fileURLWithPath:python];
    self.server.arguments = @[script, @"--no-browser"];
    self.server.currentDirectoryURL = [NSURL fileURLWithPath:self.projectPath];
    NSMutableDictionary *environment = [NSProcessInfo.processInfo.environment mutableCopy];
    environment[@"PYTHONUNBUFFERED"] = @"1";
    self.server.environment = environment;
    NSPipe *pipe = [NSPipe pipe];
    self.server.standardOutput = pipe;
    self.server.standardError = pipe;
    __weak InterfaceLauncher *weakSelf = self;
    pipe.fileHandleForReading.readabilityHandler = ^(NSFileHandle *handle) {
        NSData *data = handle.availableData;
        if (!data.length) { handle.readabilityHandler = nil; return; }
        dispatch_async(dispatch_get_main_queue(), ^{
            InterfaceLauncher *owner = weakSelf;
            if (!owner || owner.quitting) return;
            [owner.output appendData:data];
            if (owner.interfaceURL) return;
            NSString *text = [[NSString alloc] initWithData:owner.output encoding:NSUTF8StringEncoding];
            NSRegularExpression *pattern = [NSRegularExpression regularExpressionWithPattern:@"http://127\\.0\\.0\\.1:[0-9]+" options:0 error:nil];
            NSTextCheckingResult *match = [pattern firstMatchInString:text ?: @"" options:0 range:NSMakeRange(0, text.length)];
            if (match) {
                owner.interfaceURL = [text substringWithRange:match.range];
                [owner openInterface:nil];
            }
        });
    };
    self.server.terminationHandler = ^(NSTask *task) {
        dispatch_async(dispatch_get_main_queue(), ^{
            InterfaceLauncher *owner = weakSelf;
            if (owner && !owner.quitting) [owner showError:@"A interface foi encerrada inesperadamente. Reabra o aplicativo para tentar novamente."];
        });
    };
    NSError *error;
    if (![self.server launchAndReturnError:&error]) {
        [self showError:error.localizedDescription];
        return;
    }
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 15 * NSEC_PER_SEC), dispatch_get_main_queue(), ^{
        InterfaceLauncher *owner = weakSelf;
        if (owner && !owner.quitting && !owner.interfaceURL) [owner showError:@"A interface não iniciou no tempo esperado. Reabra o aplicativo para tentar novamente."];
    });
}
- (BOOL)applicationShouldHandleReopen:(NSApplication *)sender hasVisibleWindows:(BOOL)flag {
    [self openInterface:nil];
    return YES;
}
- (void)applicationWillTerminate:(NSNotification *)notification {
    self.quitting = YES;
    if (self.server.running) [self.server terminate];
}
@end

static void createIcon(NSString *path) {
    NSImage *image = [[NSImage alloc] initWithSize:NSMakeSize(1024, 1024)];
    [image lockFocus];
    [[NSColor colorWithCalibratedRed:0.09 green:0.20 blue:0.38 alpha:1] setFill];
    [[NSBezierPath bezierPathWithRoundedRect:NSMakeRect(45, 45, 934, 934) xRadius:210 yRadius:210] fill];
    [[NSColor whiteColor] setFill];
    [[NSBezierPath bezierPathWithRoundedRect:NSMakeRect(255, 165, 514, 694) xRadius:45 yRadius:45] fill];
    NSDictionary *attributes = @{NSFontAttributeName:[NSFont boldSystemFontOfSize:185], NSForegroundColorAttributeName:[NSColor colorWithCalibratedRed:0.09 green:0.20 blue:0.38 alpha:1]};
    [@"CV" drawAtPoint:NSMakePoint(369, 513) withAttributes:attributes];
    [[NSColor colorWithCalibratedRed:0.15 green:0.65 blue:0.56 alpha:1] setFill];
    for (int i=0; i<3; i++) [[NSBezierPath bezierPathWithRoundedRect:NSMakeRect(330, 425-i*90, i==2?230:364, 32) xRadius:16 yRadius:16] fill];
    [image unlockFocus];
    NSBitmapImageRep *bitmap = [[NSBitmapImageRep alloc] initWithData:image.TIFFRepresentation];
    [[bitmap representationUsingType:NSBitmapImageFileTypePNG properties:@{}] writeToFile:path atomically:YES];
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc == 3 && strcmp(argv[1], "--create-icon") == 0) {
            createIcon([NSString stringWithUTF8String:argv[2]]);
            return 0;
        }
        NSApplication *app = [NSApplication sharedApplication];
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];
        InterfaceLauncher *delegate = [[InterfaceLauncher alloc] init];
        app.delegate = delegate;
        [app run];
    }
    return 0;
}
